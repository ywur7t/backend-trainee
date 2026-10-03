from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.restaurant import Restaurant


class RestaurantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> list[Restaurant]:
        query = (
            select(Restaurant)
            .order_by(Restaurant.name)
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_by_id(self, restaurant_id: int) -> Restaurant | None:
        query = select(Restaurant).where(
            Restaurant.id == restaurant_id
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()