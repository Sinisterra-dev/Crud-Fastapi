# ============================================================
# PRACTICAS.PY - 50 misiones para entrenar logica y FastAPI
# ============================================================
# Este archivo es un laboratorio separado del CRUD principal.
# La idea es practicar fundamentos con una lista en memoria antes
# de pasar a base de datos, schemas, servicios y routers mas formales.
#
# Como usar estas misiones:
#   1. Lee la historia de usuario de cada mision.
#   2. Identifica que datos necesitas recorrer, filtrar o modificar.
#   3. Implementa la lógica usando estructuras de control básicas.
#   4. Prueba el endpoint en /docs.
# ============================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/products", tags=["products"])

products_list = [
    {
        "id": 1,
        "name": "Laptop",
        "category": "Tecnologia",
        "price": 4500,
        "stock": 8,
        "active": True,
        "sold": 22,
        "rating": 4.8,
        "discount": 10,
    },
    {
        "id": 2,
        "name": "Mouse",
        "category": "Tecnologia",
        "price": 80,
        "stock": 25,
        "active": True,
        "sold": 120,
        "rating": 4.4,
        "discount": 0,
    },
    {
        "id": 3,
        "name": "Teclado",
        "category": "Tecnologia",
        "price": 150,
        "stock": 0,
        "active": False,
        "sold": 75,
        "rating": 4.1,
        "discount": 5,
    },
    {
        "id": 4,
        "name": "Monitor",
        "category": "Tecnologia",
        "price": 1200,
        "stock": 5,
        "active": True,
        "sold": 34,
        "rating": 4.7,
        "discount": 15,
    },
    {
        "id": 5,
        "name": "Silla",
        "category": "Oficina",
        "price": 700,
        "stock": 12,
        "active": True,
        "sold": 18,
        "rating": 4.3,
        "discount": 0,
    },
    {
        "id": 6,
        "name": "Escritorio",
        "category": "Oficina",
        "price": 950,
        "stock": 3,
        "active": True,
        "sold": 9,
        "rating": 4.6,
        "discount": 20,
    },
    {
        "id": 7,
        "name": "Cuaderno",
        "category": "Papeleria",
        "price": 25,
        "stock": 60,
        "active": True,
        "sold": 210,
        "rating": 4.0,
        "discount": 0,
    },
    {
        "id": 8,
        "name": "Lapicero",
        "category": "Papeleria",
        "price": 5,
        "stock": 150,
        "active": True,
        "sold": 500,
        "rating": 3.9,
        "discount": 0,
    },
]


class ProductCreate(BaseModel):
    """Datos minimos para crear un producto desde un body JSON."""
    name: str = Field(min_length=1, max_length=80)
    category: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    active: bool = True
    rating: float = Field(default=0, ge=0, le=5)
    discount: int = Field(default=0, ge=0, le=100)


class ProductUpdate(BaseModel):
    """Todos los campos son opcionales porque PATCH actualiza parcialmente."""
    name: str | None = Field(default=None, min_length=1, max_length=80)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    active: bool | None = None
    rating: float | None = Field(default=None, ge=0, le=5)
    discount: int | None = Field(default=None, ge=0, le=100)


# ============================================================
# FUNCIONES DE APOYO (Opcional implementarlas o usarlas)
# ============================================================

def find_product(product_id: int):
    """Busca un producto por id. Retorna None si no existe."""
    for product in products_list:
        if product["id"] ==  product_id:
            return product
    return None


def next_product_id():
    """Calcula el siguiente id disponible."""
    max_id = 0

    for product in products_list:
        if product["id"] > max_id:
            max_id = product["id"]

    return max_id + 1


def product_with_discount(product):
    """Devuelve una copia con el precio final despues del descuento."""
    copy_product = product.copy()

    final_price = product ["price"] - (product ["price"] * product["discount"]/100)

    copy_product["price"] = final_price

    return copy_product


# ============================================================
# MISIONES
# ============================================================

# Mision 1
# Historia: Como administrador quiero ver solo los productos activos.
# GET /products/active
@router.get("/active")
def get_active_products():
    active_products = []
    for product in products_list:
        if product["active"]:
            active_products.append(product)
    return active_products
            


# Mision 2
# Historia: Como vendedor quiero saber que productos estan agotados (stock igual a 0).
# GET /products/out-of-stock
@router.get("/out-of-stock")
def get_out_of_stock_products():
    products_without_stock = []
    for product in products_list:
        if product["stock"] == 0:
            products_without_stock.append(product)
    return products_without_stock


# Mision 3
# Historia: Como gerente quiero ver los productos con mas de 100 ventas.
# GET /products/most-sold
@router.get("/most-sold")
def get_most_sold_products():
    products_more_100_sales = []
    for product in products_list:
        if product["sold"] > 100:
           products_more_100_sales.append(product)
    return products_more_100_sales



# Mision 4
# Historia: Como administrador quiero calcular el valor total de todo el inventario (precio * stock).
# GET /products/inventory-value
@router.get("/inventory-value")
def get_inventory_value():
    pass


# Mision 5
# Historia: Como comprador quiero saber cual es el producto mas caro del catálogo.
# GET /products/most-expensive
@router.get("/most-expensive")
def get_most_expensive():
    pass


# Mision 6 (Modificada)
# Historia: Como usuario quiero buscar un producto por nombre exacto. Si no existe, lanzar HTTPException 404.
# GET /products/search/{name}
@router.get("/search/{name}")
def search_products(name: str):
    pass


# Mision 7
# Historia: Como vendedor quiero registrar una venta, descontar stock y aumentar las unidades vendidas.
# PATCH /products/item/{id}/sell?sell=2
@router.patch("/item/{id}/sell")
def sell_products(id: int, sell: int):
    pass


# Mision 8
# Historia: Como administrador quiero ver todos los productos sin filtros.
# GET /products
@router.get("")
def get_products():
    pass


# Mision 9 (Modificada)
# Historia: Como usuario quiero obtener un producto por id. Usar HTTPException 404 si no se encuentra.
# GET /products/item/{id}
@router.get("/item/{id}")
def get_product_by_id(id: int):
    pass


# Mision 10
# Historia: Como comprador quiero ver productos con precio menor o igual a un monto máximo.
# GET /products/price/max/{max_price}
@router.get("/price/max/{max_price}")
def get_products_by_max_price(max_price: float):
    pass


# Mision 11
# Historia: Como comprador quiero ver productos dentro de un rango de precio (mínimo y máximo).
# GET /products/price/range?min_price=10&max_price=100
@router.get("/price/range")
def get_products_by_price_range(min_price: float, max_price: float):
    pass


# Mision 12
# Historia: Como administrador quiero contar cuantos productos hay activos en total.
# GET /products/count/active
@router.get("/count/active")
def count_active_products():
    pass


# Mision 13
# Historia: Como administrador quiero contar cuantos productos hay inactivos.
# GET /products/count/inactive
@router.get("/count/inactive")
def count_inactive_products():
    pass


# Mision 14
# Historia: Como gerente quiero conocer el total acumulado de unidades vendidas de toda la tienda.
# GET /products/sales/total-units
@router.get("/sales/total-units")
def get_total_sold_units():
    pass


# Mision 15
# Historia: Como gerente quiero calcular los ingresos históricos totales generados por las ventas (precio * unidades vendidas).
# GET /products/sales/revenue
@router.get("/sales/revenue")
def get_sales_revenue():
    pass


# Mision 16
# Historia: Como comprador quiero ver el producto mas barato del catálogo.
# GET /products/cheapest
@router.get("/cheapest")
def get_cheapest_product():
    pass


# Mision 17
# Historia: Como administrador quiero saber que producto tiene el stock mas alto.
# GET /products/highest-stock
@router.get("/highest-stock")
def get_highest_stock_product():
    pass


# Mision 18
# Historia: Como vendedor quiero ver productos con bajo stock, configurable mediante un límite (por defecto 5).
# GET /products/low-stock?limit=5
@router.get("/low-stock")
def get_low_stock_products(limit: int = 5):
    pass


# Mision 19
# Historia: Como comprador quiero filtrar productos pertenecientes a una categoría específica (ignorar mayúsculas/minúsculas).
# GET /products/category/{category}
@router.get("/category/{category}")
def get_products_by_category(category: str):
    pass


# Mision 20
# Historia: Como gerente quiero listar las categorias disponibles en el inventario sin elementos repetidos.
# GET /products/categories
@router.get("/categories")
def get_categories():
    pass


# Mision 21
# Historia: Como administrador quiero un conteo de cuántos productos pertenecen a cada categoría (ej: {"Tecnologia": 4, "Oficina": 2}).
# GET /products/categories/count
@router.get("/categories/count")
def count_products_by_category():
    pass


# Mision 22
# Historia: Como gerente quiero ver la sumatoria del valor de inventario agrupado por categoría.
# GET /products/categories/inventory-value
@router.get("/categories/inventory-value")
def get_inventory_value_by_category():
    pass


# Mision 23
# Historia: Como comprador quiero ver la lista de productos que tienen un descuento mayor a 0, incluyendo su precio final calculado.
# GET /products/discounted
@router.get("/discounted")
def get_discounted_products():
    pass


# Mision 24
# Historia: Como comprador quiero consultar el precio final de un producto específico aplicando su descuento correspondiente.
# GET /products/item/{id}/final-price
@router.get("/item/{id}/final-price")
def get_final_price(id: int):
    pass


# Mision 25
# Historia: Como gerente quiero calcular el promedio de precio de todos los productos del catálogo.
# GET /products/average-price
@router.get("/average-price")
def get_average_price():
    pass


# Mision 26
# Historia: Como gerente quiero calcular el promedio de calificación (rating) de los productos.
# GET /products/average-rating
@router.get("/average-rating")
def get_average_rating():
    pass


# Mision 27
# Historia: Como comprador quiero ver productos con un rating igual o superior a un mínimo dado.
# GET /products/top-rated?min_rating=4.5
@router.get("/top-rated")
def get_top_rated_products(min_rating: float = 4.5):
    pass


# Mision 28
# Historia: Como gerente quiero identificar el producto con el mejor rating de la tienda.
# GET /products/best-rated
@router.get("/best-rated")
def get_best_rated_product():
    pass


# Mision 29
# Historia: Como comprador quiero buscar productos utilizando un texto de coincidencia parcial en el nombre.
# GET /products/search-text?text=lap
@router.get("/search-text")
def search_products_by_text(text: str):
    pass


# Mision 30
# Historia: Como administrador quiero crear un producto nuevo autogenerando su ID e inicializando las ventas en 0.
# POST /products
@router.post("")
def create_product(product: ProductCreate):
    pass


# Mision 31
# Historia: Como administrador quiero actualizar parcialmente los datos de un producto (solo los campos enviados en el JSON).
# PATCH /products/item/{id}
@router.patch("/item/{id}")
def update_product(id: int, product_update: ProductUpdate):
    pass


# Mision 32
# Historia: Como administrador quiero desactivar un producto (active = False) de forma lógica, sin eliminarlo de la lista.
# PATCH /products/item/{id}/deactivate
@router.patch("/item/{id}/deactivate")
def deactivate_product(id: int):
    pass


# Mision 33
# Historia: Como administrador quiero reactivar un producto (active = True).
# PATCH /products/item/{id}/activate
@router.patch("/item/{id}/activate")
def activate_product(id: int):
    pass


# Mision 34
# Historia: Como encargado de bodega quiero incrementar el stock de un producto indicando la cantidad recibida.
# PATCH /products/item/{id}/add-stock?quantity=10
@router.patch("/item/{id}/add-stock")
def add_stock(id: int, quantity: int):
    pass


# Mision 35
# Historia: Como encargado de bodega quiero retirar unidades de stock sin que represente una venta (ej: por daño o merma).
# PATCH /products/item/{id}/remove-stock?quantity=2
@router.patch("/item/{id}/remove-stock")
def remove_stock(id: int, quantity: int):
    pass


# Mision 36
# Historia: Como administrador quiero aplicar un porcentaje de descuento a un producto (validar rango de 0 a 100).
# PATCH /products/item/{id}/discount?discount=15
@router.patch("/item/{id}/discount")
def apply_discount(id: int, discount: int):
    pass


# Mision 37
# Historia: Como administrador quiero remover por completo el descuento de un producto (dejarlo en 0).
# PATCH /products/item/{id}/clear-discount
@router.patch("/item/{id}/clear-discount")
def clear_discount(id: int):
    pass


# Mision 38
# Historia: Como comprador quiero ver el catálogo completo de productos ordenados por precio de manera ascendente.
# GET /products/sorted/price-asc
@router.get("/sorted/price-asc")
def get_products_sorted_by_price_asc():
    pass


# Mision 39
# Historia: Como comprador quiero ver el catálogo completo de productos ordenados por precio de manera descendente.
# GET /products/sorted/price-desc
@router.get("/sorted/price-desc")
def get_products_sorted_by_price_desc():
    pass


# Mision 40
# Historia: Como gerente quiero analizar el rendimiento del catálogo viendo los productos ordenados de mayor a menor número de ventas.
# GET /products/sorted/sold
@router.get("/sorted/sold")
def get_products_sorted_by_sold():
    pass


# Mision 41
# Historia: Como administrador quiero paginar los productos en memoria usando los parámetros "skip" y "limit".
# GET /products/paginated?skip=0&limit=3
@router.get("/paginated")
def get_paginated_products(skip: int = 0, limit: int = 10):
    pass


# Mision 42
# Historia: Como gerente quiero obtener un reporte consolidado del inventario (total_products, active, inactive, total_stock, inventory_value).
# GET /products/summary
@router.get("/summary")
def get_products_summary():
    pass


# Mision 43
# Historia: Como gerente quiero detectar qué productos tienen un registro de 0 unidades vendidas.
# GET /products/no-sales
@router.get("/no-sales")
def get_products_without_sales():
    pass


# Mision 44
# Historia: Como administrador quiero validar de forma rápida mediante un booleano si un nombre de producto ya existe en el catálogo.
# GET /products/exists/{name}
@router.get("/exists/{name}")
def product_name_exists(name: str):
    pass


# Mision 45
# Historia: Como administrador quiero renombrar un producto específico asegurando que el nuevo nombre no esté vacío.
# PATCH /products/item/{id}/rename?new_name=Nuevo
@router.patch("/item/{id}/rename")
def rename_product(id: int, new_name: str):
    pass


# Mision 46
# Historia: Como administrador quiero reasignar la categoría de un producto.
# PATCH /products/item/{id}/category?category=Nueva
@router.patch("/item/{id}/category")
def change_product_category(id: int, category: str):
    pass


# Mision 47
# Historia: Como gerente quiero filtrar productos de alta rentabilidad basándome en un mínimo de ventas y un stock mínimo simultáneamente.
# GET /products/profitable?sold_min=50&stock_min=1
@router.get("/profitable")
def get_profitable_products(sold_min: int = 50, stock_min: int = 1):
    pass


# Mision 48
# Historia: Como comprador quiero enviar dos IDs de producto para comparar sus precios y saber cuál es el más costoso y cuál el más económico.
# GET /products/compare-price?first_id=1&second_id=2
@router.get("/compare-price")
def compare_products_by_price(first_id: int, second_id: int):
    pass


# Mision 49
# Historia: Como administrador quiero eliminar de forma física y definitiva un producto del catálogo mediante su ID.
# DELETE /products/item/{id}
@router.delete("/item/{id}")
def delete_product(id: int):
    pass


# Mision 50 (Modificada - ¡A programar el reto!)
# Historia: Como estudiante acepto el reto final de construir el endpoint integrando múltiples filtros avanzados.
# Requisitos: Filtrar activos, categoría (case-insensitive), precio <= max_price, stock >= min_stock. Devolver total y lista.
# GET /products/challenge/filter
@router.get("/challenge/filter")
def execute_final_challenge(category: str, max_price: float, min_stock: int = 1):
    pass