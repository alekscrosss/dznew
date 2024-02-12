# файл schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class ContactBase(BaseModel):
    """
    A Pydantic base model representing the common attributes of a contact.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (EmailStr): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birthday (date): The birthday of the contact.
        additional_info (Optional[str]): Any additional information about the contact.
    """

    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    """
    A Pydantic model derived from ContactBase for creating a new contact with all the necessary information.
    """

    pass


class ContactUpdate(ContactBase):
    """
    A Pydantic model derived from ContactBase for updating an existing contact with optional information.
    """
    pass


class Contact(ContactBase):
    """
    A Pydantic model representing a contact, including its database ID.

    Attributes:
        id (int): The unique identifier of the contact in the database.
    """

    id: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """
    A Pydantic model for user creation requests.

    Attributes:
        email (EmailStr): The email address of the user.
        password (str): The password for the user.
    """

    email: str
    password: str


class UserInDB(UserCreate):
    """
    A Pydantic model for user representation in the database, extending UserCreate with a hashed password.

    Attributes:
        hashed_password (str): The hashed password for the user.
    """

    hashed_password: str


class Token(BaseModel):
    """
    A Pydantic model representing an authentication token.

    Attributes:
        access_token (str): The token that can be used for authentication.
        token_type (str): The type of the token (e.g., bearer).
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    A Pydantic model for the token data that gets encoded in an authentication token.

    Attributes:
        email (Optional[str]): The email address of the user for whom the token is issued.
    """

    email: str | None = None

class UserAvatarUpdate(BaseModel):
    """
    A Pydantic model for updating a user's avatar URL.

    Attributes:
        avatar_url (Optional[str]): The URL to the user's new avatar image.
    """

    avatar_url: Optional[str] = Field(None, description="URL аватара пользователя")