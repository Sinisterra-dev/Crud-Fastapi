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
#   3. Prueba el endpoint en /docs.
#   4. Luego intenta reescribir la solucion sin mirar la anterior.
#
# Conceptos entrenados:
#   - Listas y diccionarios
#   - for, if, acumuladores y contadores
#   - Busqueda por id, nombre, categoria y rangos
#   - Query parameters, path parameters y body JSON
#   - Metodos HTTP: GET, POST, PATCH y DELETE
#   - Validaciones basicas antes de modificar datos
# ============================================================

from fastapi import APIRouter
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


def find_product(product_id: int):
    """Busca un producto por id. Retorna None si no existe."""
    for product in products_list:
        if product["id"] == product_id:
            return product
    return None


def next_product_id():
    """Calcula el siguiente id sin depender de una base de datos."""
    max_id = 0
    for product in products_list:
        if product["id"] > max_id:
            max_id = product["id"]
    return max_id + 1


def product_with_discount(product):
    """Devuelve una copia con el precio final despues del descuento."""
    final_price = product["price"] * (1 - product["discount"] / 100)
    product_copy = product.copy()
    product_copy["final_price"] = round(final_price, 2)
    return product_copy


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
# Historia: Como vendedor quiero saber que productos estan agotados.
# GET /products/out-of-stock
@router.get("/out-of-stock")
def get_out_of_stock_products():
    out_of_stock = []
    for product in products_list:
        if product["stock"] == 0:
            out_of_stock.append(product)
    return out_of_stock


# Mision 3
# Historia: Como gerente quiero ver los productos con mas de 100 ventas.
# GET /products/most-sold
@router.get("/most-sold")
def get_most_sold_products():
    most_sold = []
    for product in products_list:
        if product["sold"] > 100:
            most_sold.append(product)
    return most_sold


# Mision 4
# Historia: Como administrador quiero calcular el valor total del inventario.
# GET /products/inventory-value
@router.get("/inventory-value")
def get_inventory_value():
    total_inventory = 0
    for product in products_list:
        total_inventory += product["price"] * product["stock"]
    return {"inventory_value": total_inventory}


# Mision 5
# Historia: Como comprador quiero saber cual es el producto mas caro.
# GET /products/most-expensive
@router.get("/most-expensive")
def get_most_expensive():
    product_max_expensive = products_list[0]
    for product in products_list:
        if product["price"] > product_max_expensive["price"]:
            product_max_expensive = product
    return product_max_expensive


# Mision 6
# Historia: Como usuario quiero buscar un producto por nombre exacto.
# GET /products/search/{name}
@router.get("/search/{name}")
def search_products(name: str):
    for product in products_list:
        if product["name"].lower() == name.lower():
            return product
    return {"error": "Product not found"}


# Mision 7
# Historia: Como vendedor quiero registrar una venta y descontar stock.
# PATCH /products/item/{id}/sell?sell=2
@router.patch("/item/{id}/sell")
def sell_products(id: int, sell: int):
    if sell <= 0:
        return {"error": "La cantidad vendida debe ser mayor que cero"}

    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}

    if product["stock"] < sell:
        return {"error": "El stock es insuficiente"}

    product["stock"] -= sell
    product["sold"] += sell
    return product


# Mision 8
# Historia: Como administrador quiero ver todos los productos.
# GET /products
@router.get("")
def get_products():
    return products_list


# Mision 9
# Historia: Como usuario quiero obtener un producto por id.
# GET /products/item/{id}
@router.get("/item/{id}")
def get_product_by_id(id: int):
    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}
    return product


# Mision 10
# Historia: Como comprador quiero ver productos con precio menor o igual a un monto.
# GET /products/price/max/{max_price}
@router.get("/price/max/{max_price}")
def get_products_by_max_price(max_price: float):
    results = []
    for product in products_list:
        if product["price"] <= max_price:
            results.append(product)
    return results


# Mision 11
# Historia: Como comprador quiero ver productos dentro de un rango de precio.
# GET /products/price/range?min_price=10&max_price=100
@router.get("/price/range")
def get_products_by_price_range(min_price: float, max_price: float):
    if min_price > max_price:
        return {"error": "min_price no puede ser mayor que max_price"}

    results = []
    for product in products_list:
        if min_price <= product["price"] <= max_price:
            results.append(product)
    return results


# Mision 12
# Historia: Como administrador quiero contar cuantos productos hay activos.
# GET /products/count/active
@router.get("/count/active")
def count_active_products():
    total = 0
    for product in products_list:
        if product["active"]:
            total += 1
    return {"active_products": total}


# Mision 13
# Historia: Como administrador quiero contar cuantos productos hay inactivos.
# GET /products/count/inactive
@router.get("/count/inactive")
def count_inactive_products():
    total = 0
    for product in products_list:
        if not product["active"]:
            total += 1
    return {"inactive_products": total}


# Mision 14
# Historia: Como gerente quiero conocer el total de unidades vendidas.
# GET /products/sales/total-units
@router.get("/sales/total-units")
def get_total_sold_units():
    total = 0
    for product in products_list:
        total += product["sold"]
    return {"total_sold_units": total}


# Mision 15
# Historia: Como gerente quiero calcular ingresos historicos por ventas.
# GET /products/sales/revenue
@router.get("/sales/revenue")
def get_sales_revenue():
    revenue = 0
    for product in products_list:
        revenue += product["price"] * product["sold"]
    return {"sales_revenue": revenue}


# Mision 16
# Historia: Como comprador quiero ver el producto mas barato.
# GET /products/cheapest
@router.get("/cheapest")
def get_cheapest_product():
    cheapest = products_list[0]
    for product in products_list:
        if product["price"] < cheapest["price"]:
            cheapest = product
    return cheapest


# Mision 17
# Historia: Como administrador quiero saber que producto tiene mas stock.
# GET /products/highest-stock
@router.get("/highest-stock")
def get_highest_stock_product():
    highest_stock = products_list[0]
    for product in products_list:
        if product["stock"] > highest_stock["stock"]:
            highest_stock = product
    return highest_stock


# Mision 18
# Historia: Como vendedor quiero ver productos con bajo stock.
# GET /products/low-stock?limit=5
@router.get("/low-stock")
def get_low_stock_products(limit: int = 5):
    results = []
    for product in products_list:
        if product["stock"] <= limit:
            results.append(product)
    return results


# Mision 19
# Historia: Como comprador quiero filtrar productos por categoria.
# GET /products/category/{category}
@router.get("/category/{category}")
def get_products_by_category(category: str):
    results = []
    for product in products_list:
        if product["category"].lower() == category.lower():
            results.append(product)
    return results


# Mision 20
# Historia: Como gerente quiero listar las categorias disponibles sin repetir.
# GET /products/categories
@router.get("/categories")
def get_categories():
    categories = []
    for product in products_list:
        if product["category"] not in categories:
            categories.append(product["category"])
    return {"categories": categories}


# Mision 21
# Historia: Como administrador quiero contar productos por categoria.
# GET /products/categories/count
@router.get("/categories/count")
def count_products_by_category():
    counters = {}
    for product in products_list:
        category = product["category"]
        if category not in counters:
            counters[category] = 0
        counters[category] += 1
    return counters


# Mision 22
# Historia: Como gerente quiero ver el valor de inventario por categoria.
# GET /products/categories/inventory-value
@router.get("/categories/inventory-value")
def get_inventory_value_by_category():
    totals = {}
    for product in products_list:
        category = product["category"]
        if category not in totals:
            totals[category] = 0
        totals[category] += product["price"] * product["stock"]
    return totals


# Mision 23
# Historia: Como comprador quiero ver productos con descuento.
# GET /products/discounted
@router.get("/discounted")
def get_discounted_products():
    results = []
    for product in products_list:
        if product["discount"] > 0:
            results.append(product_with_discount(product))
    return results


# Mision 24
# Historia: Como comprador quiero ver el precio final de un producto con descuento.
# GET /products/item/{id}/final-price
@router.get("/item/{id}/final-price")
def get_final_price(id: int):
    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}
    return product_with_discount(product)


# Mision 25
# Historia: Como gerente quiero calcular el promedio de precio.
# GET /products/average-price
@router.get("/average-price")
def get_average_price():
    total = 0
    for product in products_list:
        total += product["price"]
    return {"average_price": round(total / len(products_list), 2)}


# Mision 26
# Historia: Como gerente quiero calcular el promedio de rating.
# GET /products/average-rating
@router.get("/average-rating")
def get_average_rating():
    total = 0
    for product in products_list:
        total += product["rating"]
    return {"average_rating": round(total / len(products_list), 2)}


# Mision 27
# Historia: Como comprador quiero ver productos con rating alto.
# GET /products/top-rated?min_rating=4.5
@router.get("/top-rated")
def get_top_rated_products(min_rating: float = 4.5):
    results = []
    for product in products_list:
        if product["rating"] >= min_rating:
            results.append(product)
    return results


# Mision 28
# Historia: Como gerente quiero ver el producto con mejor rating.
# GET /products/best-rated
@router.get("/best-rated")
def get_best_rated_product():
    best = products_list[0]
    for product in products_list:
        if product["rating"] > best["rating"]:
            best = product
    return best


# Mision 29
# Historia: Como comprador quiero buscar por texto parcial en el nombre.
# GET /products/search-text?text=lap
@router.get("/search-text")
def search_products_by_text(text: str):
    results = []
    for product in products_list:
        if text.lower() in product["name"].lower():
            results.append(product)
    return results


# Mision 30
# Historia: Como administrador quiero crear un producto nuevo.
# POST /products
@router.post("")
def create_product(product: ProductCreate):
    product_dict = product.model_dump()
    product_dict["id"] = next_product_id()
    product_dict["sold"] = 0
    products_list.append(product_dict)
    return product_dict


# Mision 31
# Historia: Como administrador quiero actualizar parcialmente un producto.
# PATCH /products/item/{id}
@router.patch("/item/{id}")
def update_product(id: int, product_update: ProductUpdate):
    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}

    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        product[field] = value
    return product


# Mision 32
# Historia: Como administrador quiero desactivar un producto sin borrarlo.
# PATCH /products/item/{id}/deactivate
@router.patch("/item/{id}/deactivate")
def deactivate_product(id: int):
    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}
    product["active"] = False
    return product


# Mision 33
# Historia: Como administrador quiero reactivar un producto.
# PATCH /products/item/{id}/activate
@router.patch("/item/{id}/activate")
def activate_product(id: int):
    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}
    product["active"] = True
    return product


# Mision 34
# Historia: Como encargado de bodega quiero agregar stock.
# PATCH /products/item/{id}/add-stock?quantity=10
@router.patch("/item/{id}/add-stock")
def add_stock(id: int, quantity: int):
    if quantity <= 0:
        return {"error": "La cantidad debe ser mayor que cero"}

    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}

    product["stock"] += quantity
    return product


# Mision 35
# Historia: Como encargado de bodega quiero retirar stock sin vender.
# PATCH /products/item/{id}/remove-stock?quantity=2
@router.patch("/item/{id}/remove-stock")
def remove_stock(id: int, quantity: int):
    if quantity <= 0:
        return {"error": "La cantidad debe ser mayor que cero"}

    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}

    if product["stock"] < quantity:
        return {"error": "No hay suficiente stock"}

    product["stock"] -= quantity
    return product


# Mision 36
# Historia: Como administrador quiero aplicar descuento a un producto.
# PATCH /products/item/{id}/discount?discount=15
@router.patch("/item/{id}/discount")
def apply_discount(id: int, discount: int):
    if discount < 0 or discount > 100:
        return {"error": "El descuento debe estar entre 0 y 100"}

    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}

    product["discount"] = discount
    return product_with_discount(product)


# Mision 37
# Historia: Como administrador quiero eliminar el descuento de un producto.
# PATCH /products/item/{id}/clear-discount
@router.patch("/item/{id}/clear-discount")
def clear_discount(id: int):
    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}
    product["discount"] = 0
    return product


# Mision 38
# Historia: Como comprador quiero ver productos ordenados por precio ascendente.
# GET /products/sorted/price-asc
@router.get("/sorted/price-asc")
def get_products_sorted_by_price_asc():
    return sorted(products_list, key=lambda product: product["price"])


# Mision 39
# Historia: Como comprador quiero ver productos ordenados por precio descendente.
# GET /products/sorted/price-desc
@router.get("/sorted/price-desc")
def get_products_sorted_by_price_desc():
    return sorted(products_list, key=lambda product: product["price"], reverse=True)


# Mision 40
# Historia: Como gerente quiero ver productos ordenados por ventas.
# GET /products/sorted/sold
@router.get("/sorted/sold")
def get_products_sorted_by_sold():
    return sorted(products_list, key=lambda product: product["sold"], reverse=True)


# Mision 41
# Historia: Como administrador quiero paginar productos en memoria.
# GET /products/paginated?skip=0&limit=3
@router.get("/paginated")
def get_paginated_products(skip: int = 0, limit: int = 10):
    if skip < 0 or limit <= 0:
        return {"error": "skip debe ser >= 0 y limit debe ser > 0"}
    return {
        "total": len(products_list),
        "skip": skip,
        "limit": limit,
        "products": products_list[skip : skip + limit],
    }


# Mision 42
# Historia: Como gerente quiero un resumen general del inventario.
# GET /products/summary
@router.get("/summary")
def get_products_summary():
    active = 0
    inactive = 0
    stock = 0
    inventory_value = 0

    for product in products_list:
        if product["active"]:
            active += 1
        else:
            inactive += 1
        stock += product["stock"]
        inventory_value += product["price"] * product["stock"]

    return {
        "total_products": len(products_list),
        "active": active,
        "inactive": inactive,
        "total_stock": stock,
        "inventory_value": inventory_value,
    }


# Mision 43
# Historia: Como gerente quiero detectar productos sin ventas.
# GET /products/no-sales
@router.get("/no-sales")
def get_products_without_sales():
    results = []
    for product in products_list:
        if product["sold"] == 0:
            results.append(product)
    return results


# Mision 44
# Historia: Como administrador quiero validar si existe un nombre de producto.
# GET /products/exists/{name}
@router.get("/exists/{name}")
def product_name_exists(name: str):
    for product in products_list:
        if product["name"].lower() == name.lower():
            return {"exists": True}
    return {"exists": False}


# Mision 45
# Historia: Como administrador quiero renombrar un producto.
# PATCH /products/item/{id}/rename?new_name=Nuevo
@router.patch("/item/{id}/rename")
def rename_product(id: int, new_name: str):
    if not new_name.strip():
        return {"error": "El nuevo nombre no puede estar vacio"}

    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}

    product["name"] = new_name
    return product


# Mision 46
# Historia: Como administrador quiero cambiar la categoria de un producto.
# PATCH /products/item/{id}/category?category=Nueva
@router.patch("/item/{id}/category")
def change_product_category(id: int, category: str):
    if not category.strip():
        return {"error": "La categoria no puede estar vacia"}

    product = find_product(id)
    if product is None:
        return {"error": "Producto no encontrado"}

    product["category"] = category
    return product


# Mision 47
# Historia: Como gerente quiero ver productos rentables por minimo de ventas e inventario.
# GET /products/profitable?sold_min=50&stock_min=1
@router.get("/profitable")
def get_profitable_products(sold_min: int = 50, stock_min: int = 1):
    results = []
    for product in products_list:
        if product["sold"] >= sold_min and product["stock"] >= stock_min:
            results.append(product)
    return results


# Mision 48
# Historia: Como comprador quiero comparar dos productos por precio.
# GET /products/compare-price?first_id=1&second_id=2
@router.get("/compare-price")
def compare_products_by_price(first_id: int, second_id: int):
    first = find_product(first_id)
    second = find_product(second_id)

    if first is None or second is None:
        return {"error": "Uno de los productos no existe"}

    if first["price"] == second["price"]:
        return {"message": "Ambos productos tienen el mismo precio"}

    cheaper = first if first["price"] < second["price"] else second
    expensive = second if cheaper is first else first
    return {"cheaper": cheaper, "expensive": expensive}


# Mision 49
# Historia: Como administrador quiero eliminar un producto por id.
# DELETE /products/item/{id}
@router.delete("/item/{id}")
def delete_product(id: int):
    for index, product in enumerate(products_list):
        if product["id"] == id:
            deleted_product = products_list.pop(index)
            return deleted_product
    return {"error": "Producto no encontrado"}


# Mision 50
# Historia: Como estudiante quiero recibir un reto final para combinar varias ideas.
# GET /products/final-challenge
@router.get("/final-challenge")
def get_final_challenge():
    return {
        "mission": 50,
        "goal": "Crear un endpoint que reciba categoria, precio maximo y stock minimo.",
        "requirements": [
            "Filtrar productos activos",
            "Filtrar por categoria ignorando mayusculas",
            "Filtrar por precio menor o igual al maximo",
            "Filtrar por stock mayor o igual al minimo",
            "Devolver total y lista de productos",
        ],
        "suggested_path": "/products/challenge/filter",
    }
