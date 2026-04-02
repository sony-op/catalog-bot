import requests
from app.core.config import settings

def send_whatsapp_message(to_number: str, text: str):
    """
    Sends a WhatsApp message using Meta Cloud API.
    """
    url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": text
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code not in (200, 201):
        print(f"Failed to send WhatsApp message: {response.text}")
    return response.json()

def download_whatsapp_media(media_id: str) -> str:
    """
    Downloads an image from WhatsApp Meta Cloud API and returns local saving path.
    """
    # 1. Get media URL
    url = f"https://graph.facebook.com/v17.0/{media_id}"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return ""
    
    media_url = res.json().get("url")
    if not media_url:
        return ""
        
    # 2. Download media binary
    media_res = requests.get(media_url, headers=headers)
    if media_res.status_code == 200:
        import os
        from uuid import uuid4
        os.makedirs("tmp", exist_ok=True)
        file_path = f"tmp/{uuid4()}.jpg"
        with open(file_path, "wb") as f:
            f.write(media_res.content)
        return file_path
    
    return ""
