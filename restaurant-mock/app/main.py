from fastapi import FastAPI


app = FastAPI(
    title="Restaurant Mock API",
    version="1.0.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


RESTAURANT = {
    "external_id": "restaurant-001",
    "name": "Pizza House",
    "description": "Пицца и итальянская кухня",
    "is_open": True,
}


MENU_CATEGORIES = [
    {
        "external_id": "category-pizza",
        "name": "Пицца",
        "sort_order": 1,
    },
    {
        "external_id": "category-drinks",
        "name": "Напитки",
        "sort_order": 2,
    },
]


MENU_ITEMS = [
    {
        "external_id": "pizza-001",
        "category_external_id": "category-pizza",
        "name": "Маргарита",
        "description": "Томатный соус, моцарелла",
        "price": 650.00,
        "is_available": True,
    },
    {
        "external_id": "pizza-002",
        "category_external_id": "category-pizza",
        "name": "Пепперони",
        "description": "Томатный соус, моцарелла, пепперони",
        "price": 750.00,
        "is_available": True,
    },
    {
        "external_id": "drink-001",
        "category_external_id": "category-drinks",
        "name": "Coca-Cola",
        "description": "Coca-Cola 0.5 л",
        "price": 150.00,
        "is_available": True,
    },
]


@app.get("/api/v1/restaurant")
async def get_restaurant():
    return RESTAURANT


@app.get("/api/v1/menu")
async def get_menu():
    return {
        "categories": MENU_CATEGORIES,
        "items": MENU_ITEMS,
    }