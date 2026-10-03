from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.menu import MenuCategory, MenuItem
from app.infrastructure.database.models.restaurant import Restaurant
from app.infrastructure.integrations.restaurant_client import RestaurantClient


class RestaurantSyncService:
    def __init__(
        self,
        session: AsyncSession,
        restaurant_client: RestaurantClient,
    ) -> None:
        self.session = session
        self.restaurant_client = restaurant_client

    async def sync(self) -> Restaurant:
        restaurant_data = await self.restaurant_client.get_restaurant()
        menu_data = await self.restaurant_client.get_menu()

        restaurant = await self._sync_restaurant(restaurant_data)

        await self._sync_menu(
            restaurant=restaurant,
            menu_data=menu_data,
        )

        await self.session.commit()

        return restaurant

    async def _sync_restaurant(
        self,
        restaurant_data: dict[str, Any],
    ) -> Restaurant:
        external_id = restaurant_data["external_id"]

        query = select(Restaurant).where(
            Restaurant.external_id == external_id,
        )

        result = await self.session.execute(query)

        restaurant = result.scalar_one_or_none()

        if restaurant is None:
            restaurant = Restaurant(
                external_id=external_id,
                name=restaurant_data["name"],
                description=restaurant_data.get("description"),
                is_open=restaurant_data["is_open"],
            )

            self.session.add(restaurant)

            await self.session.flush()

            return restaurant

        restaurant.name = restaurant_data["name"]
        restaurant.description = restaurant_data.get("description")
        restaurant.is_open = restaurant_data["is_open"]

        return restaurant

    async def _sync_menu(
        self,
        restaurant: Restaurant,
        menu_data: dict[str, Any],
    ) -> None:
        categories = menu_data.get("categories", [])
        items = menu_data.get("items", [])

        category_map: dict[str, MenuCategory] = {}

        for category_data in categories:
            category = await self._sync_category(
                restaurant=restaurant,
                category_data=category_data,
            )

            category_map[category.external_id] = category

        for item_data in items:
            category_external_id = item_data["category_external_id"]

            category = category_map.get(category_external_id)

            if category is None:
                raise ValueError(
                    f"Unknown category: {category_external_id}",
                )

            await self._sync_item(
                restaurant=restaurant,
                category=category,
                item_data=item_data,
            )

    async def _sync_category(
        self,
        restaurant: Restaurant,
        category_data: dict[str, Any],
    ) -> MenuCategory:
        external_id = category_data["external_id"]

        query = select(MenuCategory).where(
            MenuCategory.restaurant_id == restaurant.id,
            MenuCategory.external_id == external_id,
        )

        result = await self.session.execute(query)

        category = result.scalar_one_or_none()

        if category is None:
            category = MenuCategory(
                restaurant_id=restaurant.id,
                external_id=external_id,
                name=category_data["name"],
                sort_order=category_data["sort_order"],
            )

            self.session.add(category)

            await self.session.flush()

            return category

        category.name = category_data["name"]
        category.sort_order = category_data["sort_order"]

        return category

    async def _sync_item(
        self,
        restaurant: Restaurant,
        category: MenuCategory,
        item_data: dict[str, Any],
    ) -> MenuItem:
        external_id = item_data["external_id"]

        query = select(MenuItem).where(
            MenuItem.restaurant_id == restaurant.id,
            MenuItem.external_id == external_id,
        )

        result = await self.session.execute(query)

        item = result.scalar_one_or_none()

        if item is None:
            item = MenuItem(
                restaurant_id=restaurant.id,
                category_id=category.id,
                external_id=external_id,
                name=item_data["name"],
                description=item_data.get("description"),
                price=Decimal(str(item_data["price"])),
                is_available=item_data["is_available"],
            )

            self.session.add(item)

            return item

        item.category_id = category.id
        item.name = item_data["name"]
        item.description = item_data.get("description")
        item.price = Decimal(str(item_data["price"]))
        item.is_available = item_data["is_available"]

        return item