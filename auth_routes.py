from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from database import Session, engine
from schemas import SignUpModel, LoginModel
from models import User
from werkzeug.security import (
    generate_password_hash, 
    check_password_hash
)

session = Session(bind=engine)

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@auth_router.get('/')
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

    return {"message": "API Authentication"}
    

@auth_router.post(
    '/signup', 
    response_model=SignUpModel, 
)
async def signup(user:SignUpModel):
    """
        ## Create a User
        This requires the following fields
        - username : string
        - email : string
        - password : string
        - is_staff : boolean
        - is_active : boolean
    """
    db_email = session.query(User).filter(User.email==user.email).first()

    if db_email is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the email already exists"
        )

    db_username = session.query(User).filter(User.username==user.username).first()

    if db_username is not None:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the username already exists"
        )
    
    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    session.add(new_user)
    session.commit()

    return new_user


@auth_router.post('/login')
async def login(user:LoginModel, Authorize:AuthJWT=Depends()):
    """
        ## Login a User
        This requires the following fields
        - username : string
        - password : string
        And return
        - Access: token
        - Refresh: refresh token
    """
    db_user = session.query(User).filter(User.username==user.username).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        response = {
            "access": access_token,
            "refresh": refresh_token
        }

        return jsonable_encoder(response)
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Invalid Username Or Password"
    )


@auth_router.post('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    """
        ## Create a fresh token
        This creates a fresh token. It requires an refresh token.
    """
    try:
        Authorize.jwt_refresh_token_requerid()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please provide a valid refresh token"
        )

    current_user = Authorize.get_jwt_subject()

    access_token = Authorize.create_access_token(subject=current_user)

    return jsonable_encoder({"access":access_token})
