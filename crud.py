# файл crud.py

from security import get_password_hash
from sqlalchemy.orm import Session
import models
import schemas
from datetime import date, timedelta
from email_verif import send_verification_email
from image_upload import upload_image

def code_generation(length=6):
    """
    Generates a random code of specified length consisting of uppercase letters and digits.

    Args:
        length (int): The length of the code to generate. Default is 6.

    Returns:
        str: A random code.
    """

    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieves a list of contacts from the database with optional pagination.

    Args:
        db (Session): The database session.
        skip (int): The number of results to skip (for pagination).
        limit (int): The maximum number of results to return.

    Returns:
        List[models.Contact]: A list of contact instances.
    """

    return db.query(models.Contact).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    """
    Creates a new contact associated with a user.

    Args:
        db (Session): The database session.
        contact (schemas.ContactCreate): The contact schema containing the contact's information.
        user_id (int): The ID of the user to whom the contact will be associated.

    Returns:
        models.Contact: The created contact instance.
    """

    new_contact = models.Contact(**contact.dict(), owner_id=user_id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def get_user_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Retrieves contacts for a specific user, with optional pagination.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose contacts to retrieve.
        skip (int): The number of results to skip (for pagination).
        limit (int): The maximum number of results to return.

    Returns:
        List[models.Contact]: A list of contacts associated with the user.
    """

    return db.query(models.Contact).filter(models.Contact.owner_id == user_id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Retrieves a single contact by ID for a specific user.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact to retrieve.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        models.Contact: The contact instance if found, otherwise None.
    """

    return db.query(models.Contact).filter(models.Contact.id == contact_id, models.Contact.owner_id == user_id).first()


def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate, user_id: int):
    """
    Updates a contact's information.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact to update.
        contact (schemas.ContactUpdate): The schema containing the contact's updated information.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        models.Contact: The updated contact instance.
    """
    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        for key, value in contact.dict(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Deletes a contact from the database.

    Args:
        db (Session): The database session.
        contact_id (int): The ID of the contact to delete.
        user_id (int): The ID of the user who owns the contact.

    Returns:
        models.Contact: The deleted contact instance, or None if the contact was not found.
    """

    db_contact = get_contact(db, contact_id, user_id)
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def get_user_by_email(db: Session, email: str):
    """
    Retrieves a user by their email address.

    Args:
        db (Session): The database session.
        email (str): The email address of the user to retrieve.

    Returns:
        models.User: The user instance if found, otherwise None.
    """

    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Creates a new user and sends a verification email.

    Args:
        db (Session): The database session.
        user (schemas.UserCreate): The schema containing the user's information.

    Returns:
        models.User: The created user instance.
    """

    fake_hashed_password = get_password_hash(user.password)
    verification_code = code_generation()
    db_user = models.User(
        email=user.email,
        hashed_password=fake_hashed_password,
        verification_code=verification_code
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


    send_verification_email(user.email, verification_code)

    return db_user


def get_upcoming_birthdays(db: Session, user_id: int, days: int = 7):
    """
    Retrieves contacts with upcoming birthdays within a specified number of days.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose contacts to check.
        days (int): The number of days within which to check for upcoming birthdays.

    Returns:
        List[models.Contact]: A list of contacts with upcoming birthdays.
    """
    today = date.today()
    end_date = today + timedelta(days=days)
    return db.query(models.Contact).filter(
        models.Contact.owner_id == user_id,
        models.Contact.birthday >= today,
        models.Contact.birthday <= end_date
    ).all()

def update_user_avatar(db: Session, user_id: int, image_file):
    """
    Updates the avatar for a specific user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose avatar is to be updated.
        image_file: The new avatar image file.

    Returns:
        models.User: The user instance with updated avatar URL, or None if the user was not found.
    """

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        avatar_url = upload_image(image_file)
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user
    return None
