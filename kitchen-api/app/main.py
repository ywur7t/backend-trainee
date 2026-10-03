from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.orders import router as orders_router
from app.api.v1.restaurants import router as restaurants_router
from app.infrastructure.database.session import get_db

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Avito.Kitchen API", version="1.0.0", description="API сервиса доставки еды")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurants_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/health/db", tags=["System"])
async def database_health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
