from fastapi import APIRouter, Request, Query, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from app.core.config import settings
from app.services.whatsapp import send_whatsapp_message, download_whatsapp_media
from app.services.gemini import analyze_product_image_and_text
from app.services.scraper import get_average_market_price
from app.services.pricing import calculate_selling_price
from app.utils.image_processing import process_product_image
from app.services.amazon_api import build_amazon_listing_payload, mock_submit_listing_to_sandbox
from app.core.database import SessionLocal
from app.models.user import User, EcomCredentials
from app.models.listing import PendingListing
import os
import uuid
import asyncio

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Meta Cloud API Webhook Verification Endpoint
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Verification fails")

def process_whatsapp_message(message_data: dict):
    """
    Background worker for processing the message
    """
    db = SessionLocal()
    try:
        messages = message_data.get("messages", [])
        if not messages:
            return
            
        message = messages[0]
        from_number = message.get("from")
        message_type = message.get("type")
        
        # 0. User DB check
        user = db.query(User).filter(User.whatsapp_phone == from_number).first()
        if not user:
            user = User(whatsapp_phone=from_number)
            db.add(user)
            db.commit()
            db.refresh(user)
            
        # Check if connected
        has_amazon = db.query(EcomCredentials).filter(EcomCredentials.user_id == user.id, EcomCredentials.platform == "amazon").first() is not None
        has_flipkart = db.query(EcomCredentials).filter(EcomCredentials.user_id == user.id, EcomCredentials.platform == "flipkart").first() is not None
        
        # Ensure base URL is set for links (use ngrok/domain in production)
        base_url = "http://localhost:8000" 
        
        if message_type == "text":
            text_body = message["text"].get("body", "").lower()
            if text_body in ("hi", "hello"):
                welcome_msg = "Welcome to WhatsApp-first AI E-commerce Manager! 🤖👔\n\n"
                if not has_amazon:
                    welcome_msg += f"🔗 *Connect Amazon:* {base_url}/api/v1/auth/connect/amazon?user_phone={from_number}\n"
                if not has_flipkart:
                    welcome_msg += f"🔗 *Connect Flipkart:* {base_url}/api/v1/auth/connect/flipkart?user_phone={from_number}\n"
                    
                if has_amazon and has_flipkart:
                    welcome_msg += "✅ Both your accounts are connected! Send me a product image to list."
                else:
                    welcome_msg += "\nPlease click the links above to connect your seller accounts."
                    
                send_whatsapp_message(from_number, welcome_msg)
                return
            elif text_body in ("1", "approve", "approve & list"):
                if not has_amazon:
                    send_whatsapp_message(from_number, "⚠️ You need to link your Amazon account first!")
                    return
                
                # Fetch pending listing
                pending = db.query(PendingListing).filter(PendingListing.user_id == user.id, PendingListing.status == "pending").order_by(PendingListing.id.desc()).first()
                if not pending:
                    send_whatsapp_message(from_number, "I couldn't find any recent product scans to list. Please send a new image!")
                    return
                
                send_whatsapp_message(from_number, "Awesome! Pushing listing to Amazon and Flipkart... 🛒")
                
                # Retrieve Credentials
                amazon_cred = db.query(EcomCredentials).filter(EcomCredentials.user_id == user.id, EcomCredentials.platform == "amazon").first()
                
                # Build payload
                payload = build_amazon_listing_payload(pending.sku, pending.ai_data, pending.pricing_data)
                
                # In FastAPI Background task, synchronous sleep is bad unless in async block, but we are inside synchronous `process_whatsapp_message`.
                # To call the async mock:
                loop = asyncio.new_event_loop()
                result = loop.run_until_complete(mock_submit_listing_to_sandbox(payload, amazon_cred.encrypted_access_token))
                
                # Update status
                pending.status = "approved"
                db.commit()
                
                send_whatsapp_message(from_number, f"✅ *Successfully Listed!*\nAmazon SKU: {pending.sku}\nListing Status: {result['status']}")
                return
            else:
                send_whatsapp_message(from_number, "Please send a clear product image to analyze, or type 'Hi' to check your connections.")
                return
        
        if message_type == "image":
            # Require auth to proceed with heavy logic?
            if not has_amazon and not has_flipkart:
                send_whatsapp_message(from_number, "⚠️ Please link at least one seller account by typing 'Hi' first.")
                return
                
            image_id = message["image"].get("id")
            caption = message["image"].get("caption", "Default product")
            
            # 1. Download
            send_whatsapp_message(from_number, "Step 1: Downloading image... 📥")
            image_path = download_whatsapp_media(image_id)
            if not image_path:
                send_whatsapp_message(from_number, "Failed to download your image. Please try again.")
                return
                
            # 2. Background Removal & Processing
            send_whatsapp_message(from_number, "Step 2: Removing background and cleaning image... ✂️")
            processed_image_path = process_product_image(image_path)
            
            # 3. Process with AI
            send_whatsapp_message(from_number, "Step 3: Analyzing product details using AI... 🧠")
            ai_data = analyze_product_image_and_text(processed_image_path, caption)
            
            if not ai_data:
                send_whatsapp_message(from_number, "AI analysis failed. Please send a clearer image.")
                return
                
            primary_keyword = ai_data.get("primary_keyword", "product")
            
            # 4. Scrape & Pricing
            send_whatsapp_message(from_number, f"Step 4: Researching market prices for '{primary_keyword}'... 🔍")
            avg_price = get_average_market_price(primary_keyword)
            pricing_data = calculate_selling_price(avg_price)
            
            # Cache the data securely in Postgres pending list
            sku = f"BOT-SKU-{uuid.uuid4().hex[:6].upper()}"
            pending = PendingListing(
                user_id=user.id,
                ai_data=ai_data,
                pricing_data=pricing_data,
                sku=sku,
                status="pending"
            )
            db.add(pending)
            db.commit()
            
            # 5. Compile Final Response
            response_text = f"✅ *Analysis Complete for: {ai_data.get('title')}*\n\n"
            response_text += "*Description:* " + ai_data.get("description", "") + "\n\n"
            if pricing_data.get("suggested_price"):
                response_text += f"💰 *Market Average:* ₹{pricing_data['market_average']}\n"
                response_text += f"🏷️ *Suggested Price:* ₹{pricing_data['suggested_price']}\n"
                response_text += f"💵 *Est. Profit (after ~15% fee & ₹60 ship):* ₹{pricing_data['estimated_profit']}\n\n"
            else:
                response_text += "❗ Could not calculate market pricing right now.\n\n"
                
            response_text += "Would you like to:\n1. Approve & List\n2. Edit Details\n\n(Reply with 1 or 2)"
                
            send_whatsapp_message(from_number, response_text)
            
            # Cleanup optionally
            try:
                os.remove(image_path)
                if processed_image_path != image_path:
                    os.remove(processed_image_path)
            except Exception:
                pass
                
        else:
            send_whatsapp_message(from_number, "Please send a clear product image to analyze.")
            
    except Exception as e:
        print(f"Error processing webhook: {e}")
    finally:
        db.close()

@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    try:
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                if "messages" in value:
                    background_tasks.add_task(process_whatsapp_message, value)
    except Exception as e:
        print(f"Webhook parsing error: {e}")
        
    return JSONResponse(content={"status": "received"}, status_code=200)
