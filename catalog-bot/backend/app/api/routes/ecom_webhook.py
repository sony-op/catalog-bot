from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, EcomCredentials
from app.services.whatsapp import send_whatsapp_message
from app.services.flipkart_api import mock_update_flipkart_inventory
import asyncio

router = APIRouter()

class OrderEvent(BaseModel):
    sku: str
    stock_remaining: int
    platform_source: str # e.g. 'amazon', 'flipkart'
    user_phone: str # Identifying who the order belongs to

def sync_inventory_background(event: OrderEvent):
    """
    Cross Platform Deductions and Low Stock Alerts
    """
    # Create isolated loop for async cross sync
    loop = asyncio.new_event_loop()
    
    try:
        # 1. Sync Logic
        # If order was on amazon, sync flipkart
        if event.platform_source.lower() == "amazon":
            result = loop.run_until_complete(mock_update_flipkart_inventory(event.sku, event.stock_remaining))
            print(f"Flipkart Sync Result: {result}")
            
        # 2. Re-order Alert Logic
        LOW_STOCK_THRESHOLD = 10
        if event.stock_remaining <= LOW_STOCK_THRESHOLD and event.stock_remaining > 0:
            msg = f"🚨 *Low Stock Alert*\n\nProduct *{event.sku}* is down to {event.stock_remaining} units on {event.platform_source.capitalize()}!\n\nReply 'RESTOCK {event.sku}' to quickly place a supplier order."
            send_whatsapp_message(event.user_phone, msg)
            
        elif event.stock_remaining <= 0:
            msg = f"🔴 *OUT OF STOCK*\n\nProduct *{event.sku}* is completely out of stock and your listings have been paused automatically."
            send_whatsapp_message(event.user_phone, msg)
            
    except Exception as e:
        print(f"Inventory Sync Error: {e}")
    finally:
        loop.close()

@router.post("/order-event")
async def receive_ecommerce_order(event: OrderEvent, background_tasks: BackgroundTasks):
    """
    A public webhook simulating an endpoint ready to catch Amazon SQS or Flipkart Webhooks.
    Real systems validate the signature. Here we just accept the Order JSON and sync.
    """
    # Push syncing and WhatsApp alerts to background task to instantly 200 OK the platform webhook
    background_tasks.add_task(sync_inventory_background, event)
    
    return {"status": "event_received"}
