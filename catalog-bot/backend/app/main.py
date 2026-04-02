from fastapi import FastAPI
from app.api.routes import webhook, auth, ecom_webhook
from app.core.database import Base, engine

# Create tables matching models
try:
    from app.models.user import User, EcomCredentials
    from app.models.listing import PendingListing
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database initialization error (likely not running Postgres): {e}")

app = FastAPI(
    title="WhatsApp-First AI E-commerce Manager",
    description="Backend for handling WhatsApp messages and Gemini AI processing for e-commerce.",
    version="1.0.0",
)

app.include_router(webhook.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(ecom_webhook.router, prefix="/api/v1/ecom")

@app.get("/health")
def health_check():
    return {"status": "ok"}
