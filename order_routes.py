from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from database import Session, engine

session = Session(bind=engine)

order_router = APIRouter(
    prefix='/orders',
    tags=['orders']
)


@order_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    """
        ## A sample message 
        This return this API is
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Inavalid Token'
        )

    return {"message": "API Orders"}
    

@order_router.post(
    '/order', 
    response_model=OrderModel, 
)
async def place_an_order(order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Placing an Order
        This requires the following fields
        - quantity : integer
        - pizza_size : string
        - order_status : string
        - flavour : string
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Inavalid Token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user).first()
    
    new_order = Order(
        pizza_size = order.pizza_size,
        order_status = order.order_status,
        flavour = order.flavour,
        quantity= order.quantity,         
    )

    new_order.user = user
    session.add(new_order)
    session.commit()

    # response = (
    #     "id": new_order.id,
    #     "quantity": new_order.quantity,
    #     "pizza_size": new_order.pizza_size,
    #     "order_status": new_order.order_status,
    #     "flavour": new_order.flavour
    # )

    return jsonable_encoder(new_order)


@order_router.get('/orders')
async def list_all_orders(Authorize:AuthJWT=Depends()):
    """
        ## List all orders
        This lists all orders made. It can be accessed by staff.
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user)

    if user.is_staff:
        orders = session.query(Order).all()
        return jsonable_encoder(orders)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="You're not a staff"
    )


@order_router.get('/orders/{id}/')
async def get_order_by_id(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Get an order by its ID
        This return an order by its ID, if is a staff.
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user)

    if user.is_staff:
        orders = session.query(Order).filter(Order.id==id).first()
        return jsonable_encoder(orders)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="User not allowed to carry out request"
    )
    

@order_router.get('/user/orders')
async def get_user_orders(Authorize:AuthJWT=Depends()):
    """
        ## Get a current user's orders
        This return list of orders by currently logged in user
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user)
    
    return jsonable_encoder(user.orders)


@order_router.get(
    '/user/order/{id}/',
    response_model=OrderModel
)
async def get_specific_order(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Get a specific order by the currently logged in user
        This return an order by ID for the currently logged in user 
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user)
    orders = user.orders

    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Order not found!"
    )


@order_router.put(
    '/order/update/{order_id}/', 
    response_model=OrderModel, 
)
async def update_order(order_id:int, order:OrderModel, Authorize:AuthJWT=Depends()):
    """
        ## Updating an Order
        This updates an order requires the following fields
        - quantity : integer
        - pizza_size : string
        - order_status : string
        - flavour : string
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    order_to_update = session.query(Order).filter(Order.id==order_id).first()
    order_to_update.quantity = order.quantity
    order_to_update.order_status = order.order_status
    order_to_update.pizza_size = order.pizza_size
    order_to_update.flavour = order.flavour

    session.commit()
    return jsonable_encoder(order_to_update)


@order_router.patch(
    '/order/update/{order_id}/', 
    response_model=OrderModel, 
)
async def update_order_status(order_id:int, order:OrderStatusModel, Authorize:AuthJWT=Depends()):
    """
        ## Update an Order's status
        This is for updating an order's status and requires the following fields
        - order_status : string
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user)

    if user.is_staff:
        order_to_update = session.query(Order).filter(Order.id==order_id).first()
        order_to_update.order_status = order.order_status

        session.commit()
        return jsonable_encoder(order_to_update)

        
@order_router.delete(
    '/order/delete/{order_id}/',
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_order_status(order_id:int, Authorize:AuthJWT=Depends()):
    """
        ## Delete an Order
        This deletes an order by its ID
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    order_to_delete = session.query(Order).filter(Order.id==order_id).first()
    session.delete(order_to_delete)
    session.commit()

    return order_to_delete