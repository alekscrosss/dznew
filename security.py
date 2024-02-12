# файл security.py


from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

from models import User, get_db

# Configuration for JWT token generation and verification
SECRET_KEY = "Bjgji6930"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Cryptographic context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer token instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    """
    Pydantic model to validate the data in a JWT token.

    Attributes:
        email (str | None): The email extracted from the token payload, if any.
    """
    email: str | None = None

def get_password_hash(password):
    """
    Generates a password hash using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: A hashed version of the password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """
    Verifies a password against its hashed version.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT token with the given data and expiry.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): The amount of time until the token expires.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """
    Validates a JWT token and returns the email contained in the token data.

    Args:
        token (str): The JWT token to verify.
        credentials_exception (HTTPException): The exception to raise if verification fails.

    Returns:
        TokenData: The email address contained in the token.

    Raises:
        credentials_exception: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    return token_data

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user by their email and password.

    Args:
        db (Session): The SQLAlchemy session to use for the database lookup.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        User | bool: The authenticated user model if authentication is successful; False otherwise.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current user based on the token.

    Args:
        token (str): The OAuth2 token.
        db (Session): The SQLAlchemy session to use for the database lookup.

    Returns:
        User: The user model instance of the authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user
