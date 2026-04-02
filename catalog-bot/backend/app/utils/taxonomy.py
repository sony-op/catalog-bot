def map_keyword_to_amazon_category(primary_keyword: str) -> dict:
    """
    Maps an AI-generated product type (e.g. "shirt") to Amazon's exact 
    ProductType requirement for JSON Listings.
    Uses a small local mock taxonomy for testing phases.
    """
    keyword = primary_keyword.lower()
    
    # Very basic static taxonomy matching
    taxonomy = {
        "shirt": {"product_type": "SHIRT", "node_id": "1968120031"},
        "tshirt": {"product_type": "SHIRT", "node_id": "1968120031"},
        "jeans": {"product_type": "PANTS", "node_id": "1968076031"},
        "pants": {"product_type": "PANTS", "node_id": "1968076031"},
        "shoes": {"product_type": "SHOES", "node_id": "1983518031"},
        "bag": {"product_type": "BAG", "node_id": "1983350031"},
    }
    
    for key, data in taxonomy.items():
        if key in keyword:
            return data
            
    # Default fallback
    return {"product_type": "PRODUCT", "node_id": "unknown"}
