from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class OrderItemCreate(BaseModel):
    menu_item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)

class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    restaurant_id: int = Field(gt=0)
    address_id: int = Field(gt=0)
    delivery_type_id: int = Field(gt=0)
    items: list[OrderItemCreate] = Field(min_length=1, max_length=100)

class OrderStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=100)

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    menu_item_id: int
    name: str
    quantity: int
    price_per_item: Decimal
    total_price: Decimal

class DeliveryAddressResponse(BaseModel):
    city: str
    street: str
    house: str
    apartment: str | None
    floor: str | None

class RestaurantShortResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class OrderResponse(BaseModel):
    id: int
    status: str
    restaurant: RestaurantShortResponse
    delivery_type: str
    delivery_address: DeliveryAddressResponse
    items: list[OrderItemResponse]
    total_price: Decimal
    created_at: datetime
