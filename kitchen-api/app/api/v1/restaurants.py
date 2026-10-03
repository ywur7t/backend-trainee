from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.restaurant_sync import RestaurantSyncService
from app.infrastructure.database.models.menu import MenuCategory, MenuItem
from app.infrastructure.database.models.restaurant import Restaurant
from app.infrastructure.database.session import get_db
from app.infrastructure.integrations.restaurant_client import RestaurantClient
from app.config import settings
from app.schemas.restaurant import RestaurantResponse, RestaurantMenuResponse, MenuCategoryResponse, MenuItemResponse

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

@router.get("", response_model=list[RestaurantResponse])
async def get_restaurants(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Restaurant).order_by(Restaurant.name))
    return list(result.scalars().all())

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(restaurant_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = result.scalar_one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.get("/{restaurant_id}/menu", response_model=RestaurantMenuResponse)
async def get_menu(restaurant_id: int, session: AsyncSession = Depends(get_db)):
    restaurant_result = await session.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = restaurant_result.scalar_one_or_none()
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    cat_result = await session.execute(select(MenuCategory).where(MenuCategory.restaurant_id == restaurant_id).order_by(MenuCategory.sort_order, MenuCategory.name))
    item_result = await session.execute(select(MenuItem).where(MenuItem.restaurant_id == restaurant_id).order_by(MenuItem.name))
    return RestaurantMenuResponse(restaurant_id=restaurant.id, restaurant_name=restaurant.name, categories=[MenuCategoryResponse.model_validate(x) for x in cat_result.scalars().all()], items=[MenuItemResponse.model_validate(x) for x in item_result.scalars().all()])

@router.post("/sync", response_model=RestaurantResponse)
async def sync_restaurant(session: AsyncSession = Depends(get_db)):
    try:
        service = RestaurantSyncService(session=session, restaurant_client=RestaurantClient(settings.restaurant_mock_url))
        restaurant = await service.sync()
        await session.refresh(restaurant)
        return restaurant
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
