from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DeliveryType(Base):
    __tablename__ = "delivery_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    orders: Mapped[list["Order"]] = relationship(back_populates="delivery_type")


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    orders: Mapped[list["Order"]] = relationship(back_populates="status")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("total_price >= 0", name="ck_orders_total_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    delivery_type_id: Mapped[int] = mapped_column(ForeignKey("delivery_types.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("order_statuses.id"), nullable=False)
    delivery_city: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_street: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_house: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_apartment: Mapped[str | None] = mapped_column(String(255))
    delivery_floor: Mapped[str | None] = mapped_column(String(255))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, server_default="CURRENT_TIMESTAMP")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now, server_default="CURRENT_TIMESTAMP")

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    restaurant: Mapped["Restaurant"] = relationship(back_populates="orders")
    address: Mapped["Address"] = relationship(back_populates="orders")
    delivery_type: Mapped["DeliveryType"] = relationship(back_populates="orders")
    status: Mapped["OrderStatus"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("price_per_item >= 0", name="ck_order_items_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_item: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    @property
    def total_price(self) -> Decimal:
        return self.price_per_item * self.quantity

    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship(back_populates="order_items")
