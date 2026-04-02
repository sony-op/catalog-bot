import uuid
from app.utils.taxonomy import map_keyword_to_amazon_category
import asyncio

def build_amazon_listing_payload(sku: str, ai_data: dict, pricing_data: dict, image_url: str = "https://example.com/placeholder.jpg") -> dict:
    """
    Constructs the stringent Amazon SP-API JSON Listing format based on 
    the dynamically calculated AI and Costing definitions.
    """
    keyword = ai_data.get("primary_keyword", "")
    taxonomy = map_keyword_to_amazon_category(keyword)
    
    price = pricing_data.get("suggested_price", 0.0)
    
    bullet_points = [{"value": bp, "language_tag": "en_IN"} for bp in ai_data.get("bullet_points", [])]
    
    payload = {
        "productType": taxonomy["product_type"],
        "attributes": {
            "item_name": [
                {
                    "value": ai_data.get("title", f"New {keyword} Product"),
                    "language_tag": "en_IN"
                }
            ],
            "product_description": [
                {
                    "value": ai_data.get("description", ""),
                    "language_tag": "en_IN"
                }
            ],
            "bullet_point": bullet_points,
            "recommended_browse_nodes": [
                {
                    "value": taxonomy["node_id"]
                }
            ],
            "purchasable_offer": [
                {
                    "currency": "INR",
                    "our_price": [
                        {
                            "schedule": [
                                {
                                    "value_with_tax": price
                                }
                            ]
                        }
                    ]
                }
            ],
            "main_product_image_locator": [
                {
                    "media_location": image_url
                }
            ]
        }
    }
    
    return payload

async def mock_submit_listing_to_sandbox(payload: dict, credentials_token: str) -> dict:
    """
    Simulates making the PUT call to: https://sandbox.sellingpartnerapi-eu.amazon.com/listings/2021-08-01/items/{sellerId}/{sku}
    """
    # Simply mocking a realistic delay for the AWS SigV4 / Auth / PUT pipeline
    await asyncio.sleep(2.5) 
    
    # Return mock success structure
    return {
        "sku": str(uuid.uuid4()),
        "status": "ACCEPTED",
        "submissionId": str(uuid.uuid4()),
        "issues": []
    }
