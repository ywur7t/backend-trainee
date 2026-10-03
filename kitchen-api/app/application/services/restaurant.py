from app.infrastructure.database.models.restaurant import Restaurant
from app.infrastructure.database.repositories.restaurant import RestaurantRepository


class RestaurantService:
    def __init__(
        self,
        repository: RestaurantRepository,
    ) -> None:
        self.repository = repository

    async def get_restaurants(self) -> list[Restaurant]:
        return await self.repository.get_all()

    async def get_restaurant(
        self,
        restaurant_id: int,
    ) -> Restaurant | None:
        return await self.repository.get_by_id(restaurant_id)