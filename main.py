import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Customer, Order, Inquiry


app = FastAPI(title="Medicine Distribution API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Medicine Distribution API running"}


@app.get("/test")
def test_database():
    """Connectivity check for database and env vars"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "❌ Unknown"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:100]}"

    return response


# ---------- Schema Exposure (for tooling) ----------
class SchemaInfo(BaseModel):
    name: str
    fields: dict


@app.get("/schema")
def get_schema():
    from schemas import Product, Customer, Order, Inquiry

    def to_dict(model):
        return {k: str(v.annotation) for k, v in model.model_fields.items()}

    return {
        "product": to_dict(Product),
        "customer": to_dict(Customer),
        "order": to_dict(Order),
        "inquiry": to_dict(Inquiry),
    }


# ---------- Catalog Endpoints ----------
@app.post("/products")
def create_product(product: Product):
    inserted_id = create_document("product", product)
    return {"id": inserted_id}


@app.get("/products")
def list_products():
    docs = get_documents("product")
    # Convert ObjectId to string
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# ---------- Inquiry Endpoint ----------
@app.post("/inquiries")
def create_inquiry(inquiry: Inquiry):
    inserted_id = create_document("inquiry", inquiry)
    return {"id": inserted_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
