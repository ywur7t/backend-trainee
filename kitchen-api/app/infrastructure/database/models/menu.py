from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class MenuCategory(Base):
    __tablename__ = "menu_categories"

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "external_id",
            name="uq_menu_categories_restaurant_external_id",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"),
        nullable=False,
    )

    external_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    restaurant: Mapped["Restaurant"] = relationship(
        back_populates="menu_categories",
    )

    menu_items: Mapped[list["MenuItem"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )

class MenuItem(Base):
    __tablename__ = "menu_items"

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id",
            "external_id",
            name="uq_menu_items_restaurant_external_id",
        ),
        CheckConstraint(
            "price >= 0",
            name="ck_menu_items_price_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"),
        nullable=False,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("menu_categories.id"),
        nullable=False,
    )

    external_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    restaurant: Mapped["Restaurant"] = relationship(
        back_populates="menu_items",
    )

    category: Mapped["MenuCategory"] = relationship(
        back_populates="menu_items",
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="menu_item",
    )