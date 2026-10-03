from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.order import OrderService
from app.infrastructure.database.session import get_db
from app.schemas.order import (DeliveryAddressResponse, OrderCreate, OrderItemResponse, OrderResponse, RestaurantShortResponse, OrderStatusUpdate)

router = APIRouter(prefix="/orders", tags=["Orders"])

def _response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id, status=order.status.name,
        restaurant=RestaurantShortResponse(id=order.restaurant.id, name=order.restaurant.name),
        delivery_type=order.delivery_type.name,
        delivery_address=DeliveryAddressResponse(city=order.delivery_city, street=order.delivery_street, house=order.delivery_house, apartment=order.delivery_apartment, floor=order.delivery_floor),
        items=[OrderItemResponse(menu_item_id=i.menu_item_id, name=i.name, quantity=i.quantity, price_per_item=i.price_per_item, total_price=i.total_price) for i in order.items],
        total_price=order.total_price, created_at=order.created_at,
    )

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, session: AsyncSession = Depends(get_db)) -> OrderResponse:
    try:
        return _response(await OrderService(session).create_order(data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, session: AsyncSession = Depends(get_db)) -> OrderResponse:
    try:
        return _response(await OrderService(session).get_order(order_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: int, data: OrderStatusUpdate, session: AsyncSession = Depends(get_db)) -> OrderResponse:
    try:
        return _response(await OrderService(session).update_status(order_id, data.status))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
