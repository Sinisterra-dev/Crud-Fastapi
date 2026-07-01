#Codigo
from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])

products_list = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 4500,
        "stock": 8,
        "active": True,
        "sold": 22
    },
    {
        "id": 2,
        "name": "Mouse",
        "price": 80,
        "stock": 25,
        "active": True,
        "sold": 120
    },
    {
        "id": 3,
        "name": "Teclado",
        "price": 150,
        "stock": 0,
        "active": False,
        "sold": 75
    },
    {
        "id": 4,
        "name": "Monitor",
        "price": 1200,
        "stock": 5,
        "active": True,
        "sold": 34
    }
]

