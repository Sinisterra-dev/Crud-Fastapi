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
#Historia de usuario
##Como administrador quiero ver únicamente los productos que están activos.

activos = []

for product in products_list:
    if product["active"]:
        activos.append(product) 
print(activos)

#JSON
@router.get("/active")
def get_active_products():
    activos = []

    for product in products_list:
        if product["active"]:
            activos.append(product)
            
    return activos

#Mision 2
##GET /products/out-of-stock con stock ==0

@router.get("/out-of-stock")
def get_out_of_stock_products():
    out_of_stock = []

    for product in products_list:
        if product["stock"] == 0:
            out_of_stock.append(product)

    return out_of_stock


#Mision 3
##GET /products/most-sold con sold > 1000    
@router.get("/most-sold")
def get_most_sold_products():
    most_sold = []

    for product in products_list:
        if product["sold"] > 100:
            most_sold.append(product)

    return most_sold
