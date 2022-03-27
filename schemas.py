from pydantic import BaseModel
from typing import Optional

class SignUpModel(BaseModel):
    id: Optional[str]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                "username": "John Snow",
                "email": "johnsnow@dragon.com",
                "password": "1234",
                "is_staff": True,
                "is_active": True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str='399bfd98987bcd24063659d00afc059262d09d045ed184d7c3e6d5d900817e69'

class LoginModel(BaseModel):
    username: str
    password: str

class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = 'PENDING'
    pizza_size: Optional[str] = 'SMALL'
    flavour: Optional[str] = 'PEPPERONI'
    user_id: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 2,
                "order_status": 'PENDING',
                "pizza_size": 'SMALL',
                "flavour": 'PEPPERONI'
            }
        }

class OrderStatusModel(BaseModel):
    order_status: Optional[str] = 'PENDING'

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "order_status": 'PENDING'
            }
        }
