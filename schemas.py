"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import date

# Core domain schemas for the Auto Trader app

class Dealer(BaseModel):
    """
    Dealers collection schema
    Collection name: "dealer"
    """
    name: str = Field(..., description="Dealer or seller name")
    email: str = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    city: Optional[str] = Field(None)
    state: Optional[str] = Field(None)
    rating: Optional[float] = Field(4.5, ge=0, le=5)

class Car(BaseModel):
    """
    Cars collection schema
    Collection name: "car"
    """
    make: str = Field(..., description="Manufacturer, e.g. Tesla")
    model: str = Field(..., description="Model, e.g. Model 3")
    year: int = Field(..., ge=1900, le=2100)
    price: float = Field(..., ge=0)
    mileage: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field("Gasoline")
    transmission: Optional[str] = Field("Automatic")
    body_style: Optional[str] = Field(None)
    color: Optional[str] = Field(None)
    location: Optional[str] = Field(None)
    features: List[str] = Field(default_factory=list)
    photos: List[HttpUrl] = Field(default_factory=list)
    dealer_id: Optional[str] = Field(None, description="Reference to dealer")
    listed_on: Optional[date] = Field(None, description="Listing date")
    condition: Optional[str] = Field("Used")

class Lead(BaseModel):
    """
    Leads collection schema
    Collection name: "lead"
    """
    car_id: str = Field(..., description="Interested car id")
    name: str = Field(...)
    email: str = Field(...)
    phone: Optional[str] = None
    message: Optional[str] = None

# Example schemas kept for reference
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
