import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Car, Dealer, Lead

app = FastAPI(title="Auto Trader API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities
class ObjectIdStr(BaseModel):
    id: str


def validate_object_id(oid: str) -> ObjectId:
    try:
        return ObjectId(oid)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id format")


@app.get("/")
def read_root():
    return {"message": "Auto Trader Backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Car Endpoints
@app.post("/api/cars", response_model=dict)
def create_car(car: Car):
    try:
        new_id = create_document("car", car)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cars", response_model=List[dict])
def list_cars(make: Optional[str] = None, model: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None, limit: int = 20):
    query = {}
    if make:
        query["make"] = {"$regex": f"^{make}$", "$options": "i"}
    if model:
        query["model"] = {"$regex": f"^{model}$", "$options": "i"}
    price_filter = {}
    if min_price is not None:
        price_filter["$gte"] = min_price
    if max_price is not None:
        price_filter["$lte"] = max_price
    if price_filter:
        query["price"] = price_filter

    try:
        docs = get_documents("car", query, limit)
        # Convert ObjectId to string and datetime to isoformat
        def normalize(d):
            d["id"] = str(d.pop("_id")) if d.get("_id") else None
            for k, v in list(d.items()):
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
            return d
        return [normalize(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cars/seed", response_model=dict)
def seed_cars():
    """Insert a small set of sample cars for demo purposes"""
    try:
        samples = [
            Car(make="Tesla", model="Model 3", year=2022, price=32990, mileage=12000, fuel_type="Electric", transmission="Automatic", body_style="Sedan", color="White", location="San Francisco, CA", features=["Autopilot", "Heated Seats", "Panoramic Roof"], photos=["https://images.unsplash.com/photo-1552519507-da3b142c6e3d"]),
            Car(make="BMW", model="X5", year=2020, price=38950, mileage=24000, fuel_type="Gasoline", transmission="Automatic", body_style="SUV", color="Black", location="New York, NY", features=["xDrive AWD", "Leather", "HUD"], photos=["https://images.unsplash.com/photo-1549924231-f129b911e442"]),
            Car(make="Toyota", model="Camry", year=2019, price=18990, mileage=36000, fuel_type="Hybrid", transmission="Automatic", body_style="Sedan", color="Blue", location="Austin, TX", features=["Adaptive Cruise", "Lane Assist"], photos=["https://images.unsplash.com/photo-1503376780353-7e6692767b70"]),
            Car(make="Audi", model="A4", year=2021, price=29950, mileage=18000, fuel_type="Gasoline", transmission="Automatic", body_style="Sedan", color="Gray", location="Seattle, WA", features=["Quattro", "Virtual Cockpit"], photos=["https://images.unsplash.com/photo-1511919884226-fd3cad34687c"]),
        ]
        inserted = []
        for c in samples:
            inserted.append(create_document("car", c))
        return {"inserted": inserted, "count": len(inserted)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Dealer Endpoints
@app.post("/api/dealers", response_model=dict)
def create_dealer(dealer: Dealer):
    try:
        new_id = create_document("dealer", dealer)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dealers", response_model=List[dict])
def list_dealers(limit: int = 50):
    try:
        docs = get_documents("dealer", {}, limit)
        def normalize(d):
            d["id"] = str(d.pop("_id")) if d.get("_id") else None
            return d
        return [normalize(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Lead Endpoints
@app.post("/api/leads", response_model=dict)
def create_lead(lead: Lead):
    try:
        new_id = create_document("lead", lead)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hello")
def hello():
    return {"message": "Hello from Auto Trader backend!"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
