from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.customer import Address, Customer
from app.infrastructure.database.models.menu import MenuItem
from app.infrastructure.database.models.order import DeliveryType, Order, OrderItem, OrderStatus
from app.infrastructure.database.models.restaurant import Restaurant
from app.schemas.order import OrderCreate


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_order(self, data: OrderCreate) -> Order:
        customer = await self._get_customer(data.customer_id)
        restaurant = await self._get_restaurant(data.restaurant_id)
        address = await self._get_address(data.address_id, customer.id)
        delivery_type = await self._get_delivery_type(data.delivery_type_id)
        status = await self._get_status("NEW")

        now = datetime.now(timezone.utc)
        order = Order(
            customer_id=customer.id, restaurant_id=restaurant.id, address_id=address.id,
            delivery_type_id=delivery_type.id, status_id=status.id,
            delivery_city=address.city, delivery_street=address.street,
            delivery_house=address.house, delivery_apartment=address.apartment,
            delivery_floor=address.floor, total_price=Decimal("0.00"),
            created_at=now, updated_at=now,
        )
        self.session.add(order)

        total = Decimal("0.00")
        for item_data in data.items:
            menu_item = await self._get_menu_item(item_data.menu_item_id, restaurant.id)
            if not menu_item.is_available:
                raise ValueError(f"Menu item '{menu_item.name}' is unavailable")
            item = OrderItem(
                order=order, menu_item_id=menu_item.id, name=menu_item.name,
                quantity=item_data.quantity, price_per_item=menu_item.price,
            )
            total += menu_item.price * item_data.quantity

        order.total_price = total
        await self.session.commit()
        return await self.get_order(order.id)

    async def get_order(self, order_id: int) -> Order:
        query = (select(Order).where(Order.id == order_id).options(
            selectinload(Order.status), selectinload(Order.restaurant),
            selectinload(Order.delivery_type), selectinload(Order.items),
        ))
        result = await self.session.execute(query)
        order = result.scalar_one_or_none()
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        return order

    async def update_status(self, order_id: int, status_name: str) -> Order:
        order = await self.get_order(order_id)
        status = await self._get_status(status_name)
        order.status_id = status.id
        order.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        return await self.get_order(order.id)

    async def _get_customer(self, customer_id: int) -> Customer:
        result = await self.session.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if customer is None:
            raise ValueError(f"Customer {customer_id} not found")
        return customer

    async def _get_restaurant(self, restaurant_id: int) -> Restaurant:
        result = await self.session.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
        restaurant = result.scalar_one_or_none()
        if restaurant is None:
            raise ValueError(f"Restaurant {restaurant_id} not found")
        if not restaurant.is_open:
            raise ValueError("Restaurant is currently closed")
        return restaurant

    async def _get_address(self, address_id: int, customer_id: int) -> Address:
        result = await self.session.execute(select(Address).where(Address.id == address_id, Address.customer_id == customer_id))
        address = result.scalar_one_or_none()
        if address is None:
            raise ValueError(f"Address {address_id} does not belong to customer {customer_id}")
        return address

    async def _get_delivery_type(self, delivery_type_id: int) -> DeliveryType:
        result = await self.session.execute(select(DeliveryType).where(DeliveryType.id == delivery_type_id))
        value = result.scalar_one_or_none()
        if value is None:
            raise ValueError(f"Delivery type {delivery_type_id} not found")
        return value

    async def _get_status(self, status_name: str) -> OrderStatus:
        result = await self.session.execute(select(OrderStatus).where(OrderStatus.name == status_name))
        value = result.scalar_one_or_none()
        if value is None:
            raise ValueError(f"Order status '{status_name}' not found")
        return value

    async def _get_menu_item(self, menu_item_id: int, restaurant_id: int) -> MenuItem:
        result = await self.session.execute(select(MenuItem).where(MenuItem.id == menu_item_id, MenuItem.restaurant_id == restaurant_id))
        value = result.scalar_one_or_none()
        if value is None:
            raise ValueError(f"Menu item {menu_item_id} not found in restaurant {restaurant_id}")
        return value
