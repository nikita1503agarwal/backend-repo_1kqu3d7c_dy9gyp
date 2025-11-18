"""
Database Schemas for Medicine Distribution App

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., Product -> "product").

These schemas are used for validation on create/update and are also exposed via
GET /schema for tooling.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class Product(BaseModel):
    """
    Pharmaceuticals catalog
    Collection: "product"
    """
    name: str = Field(..., description="Product commercial name")
    sku: str = Field(..., description="Internal SKU or code")
    dosage_form: str = Field(..., description="e.g., tablet, capsule, injection")
    strength: str = Field(..., description="e.g., 500 mg, 5 mg/mL")
    manufacturer: str = Field(..., description="Manufacturer name")
    therapeutic_class: Optional[str] = Field(None, description="Therapeutic category")
    rx_required: bool = Field(True, description="Prescription required")
    cold_chain: bool = Field(False, description="Requires cold-chain handling")
    price: float = Field(..., ge=0, description="Unit price")
    stock: int = Field(..., ge=0, description="Units in stock")


class Customer(BaseModel):
    """
    B2B customers (pharmacies, clinics, hospitals)
    Collection: "customer"
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    organization_type: Optional[str] = Field(
        None, description="pharmacy | clinic | hospital | distributor | other"
    )
    address: Optional[str] = None


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0)


class Order(BaseModel):
    """
    Customer orders
    Collection: "order"
    """
    customer_name: str
    customer_email: EmailStr
    items: List[OrderItem]
    subtotal: float = Field(..., ge=0)
    tax: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
    notes: Optional[str] = None


class Inquiry(BaseModel):
    """
    Contact and RFQ inquiries from landing page
    Collection: "inquiry"
    """
    name: str
    email: EmailStr
    message: str
    company: Optional[str] = None
    phone: Optional[str] = None
