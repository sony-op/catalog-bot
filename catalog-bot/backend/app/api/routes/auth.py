from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, EcomCredentials
from app.utils.security import encrypt_token
from app.services.whatsapp import send_whatsapp_message
import uuid

router = APIRouter()

@router.get("/connect/{platform}", response_class=HTMLResponse)
def connect_platform(platform: str, user_phone: str = Query(...)):
    """
    Mock endpoint that acts like the OAuth redirect for Amazon/Flipkart
    """
    if platform not in ["amazon", "flipkart"]:
        raise HTTPException(status_code=400, detail="Invalid platform")
        
    return f"""
    <html>
        <head><title>Connect {platform.capitalize()}</title></head>
        <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h2>Connect your {platform.capitalize()} Seller Account</h2>
            <p>Clicking the button below will simulate a successful OAuth connection.</p>
            <form action="/api/v1/auth/callback/{platform}" method="POST">
                <input type="hidden" name="user_phone" value="{user_phone}">
                <button type="submit" style="padding: 10px 20px; font-size: 16px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Authorize {platform.capitalize()}
                </button>
            </form>
        </body>
    </html>
    """

@router.post("/callback/{platform}")
def oauth_callback(platform: str, user_phone: str = Query(...), db: Session = Depends(get_db)):
    """
    Simulates receiving the tokens and saving them encrypted sequentially to the User object.
    """
    # Find user
    user = db.query(User).filter(User.whatsapp_phone == user_phone).first()
    if not user:
        return HTMLResponse("<h2>Error: User not found. Please message the bot again on WhatsApp.</h2>", status_code=404)
        
    # Mock tokens that we would normally get from Amazon SP-API or Flipkart API
    fake_access_token = f"mock_access_{uuid.uuid4().hex}"
    fake_refresh_token = f"mock_refresh_{uuid.uuid4().hex}"
    fake_seller_id = f"A{uuid.uuid4().hex[:10].upper()}"
    
    # Encrypt
    enc_access = encrypt_token(fake_access_token)
    enc_refresh = encrypt_token(fake_refresh_token)
    
    # Save to db
    cred = db.query(EcomCredentials).filter(EcomCredentials.user_id == user.id, EcomCredentials.platform == platform).first()
    if cred:
        # Update existing
        cred.encrypted_access_token = enc_access
        cred.encrypted_refresh_token = enc_refresh
        cred.seller_id = fake_seller_id
    else:
        # Insert new
        cred = EcomCredentials(
            user_id=user.id,
            platform=platform,
            encrypted_access_token=enc_access,
            encrypted_refresh_token=enc_refresh,
            seller_id=fake_seller_id
        )
        db.add(cred)
        
    db.commit()
    
    # Notify user on whatsapp
    send_whatsapp_message(user_phone, f"✅ Excellent! Your {platform.capitalize()} account (Seller ID: {fake_seller_id}) has been securely linked and tokens are encrypted.\n\nYou can now send me a product photo to list!")
    
    return HTMLResponse(f"<h2>Success! Your {platform.capitalize()} account was linked safely.</h2><p>You can close this window and return to WhatsApp.</p>")
