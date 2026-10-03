from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MenuCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int


class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    name: str
    description: str | None
    price: Decimal
    is_available: bool
    category_id: int


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    name: str
    description: str | None
    is_open: bool


class RestaurantDetailResponse(RestaurantResponse):
    menu_categories: list[MenuCategoryResponse] = Field(default_factory=list)


class RestaurantMenuResponse(BaseModel):
    restaurant_id: int
    restaurant_name: str
    categories: list[MenuCategoryResponse]
    items: list[MenuItemResponse]