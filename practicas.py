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

# Misiópn 4 Valor total del inventario
# GET /products/inventory-value

@router.get("/inventory-value")
def get_inventory_value():
    total_inventory = 0

    for product in products_list:
        total_inventory += product["price"] * product["stock"]
      

    return {
    "inventory_value": total_inventory
}

#Misión 5
##Como administrador quiero saber cuál es el producto más caro.
#GET /products/most-expensive


@router.get("/most-expensive")
def get_most_expensive():
    product_max_expensive = products_list[0]

    for product in products_list:
        if product["price"] >  product_max_expensive["price"]:
            product_max_expensive = product
      

    return product_max_expensive
    

#Misión 6 - Buscar por nombre
#GET /products/search/{name}

@router.get("/search/{name}")
def search_products(name: str):
    for product in products_list:
        if product["name"].lower() ==  name.lower():
            return product

    return {
    "error": "Product not found"
}


#Mision 7
# PATCH /products/{id}/sell

