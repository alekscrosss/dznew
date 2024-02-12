# файл main.py

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
from models import User, get_db, engine
from schemas import UserCreate, Token, Contact
from security import create_access_token, get_current_user, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import timedelta


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)

load_dotenv()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/{user_id}/avatar")
def update_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):

    """
    Updates the avatar for a specific user.

    Args:
        user_id (int): The ID of the user whose avatar is to be updated.
        file (UploadFile): The new avatar image.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.
        current_user (models.User, optional): Dependency that retrieves the currently authenticated user.

    Raises:
        HTTPException: If the user ID does not match the current user's ID.

    Returns:
        The updated user model with the new avatar URL.
    """

    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user's avatar")
    return crud.update_user_avatar(db=db, user_id=user_id, image_file=file.file)

@app.get("/verify/{verification_code}")
def verify_email(verification_code: str, db: Session = Depends(get_db)):
    """
    Verifies a user's email address using a verification code.

    Args:
        verification_code (str): The verification code sent to the user's email.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.

    Raises:
        HTTPException: If no user is found with the provided verification code.

    Returns:
        dict: A message indicating successful email verification.
    """

    user = db.query(models.User).filter(models.User.verification_code == verification_code).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    user.verification_code = None  #
    db.commit()
    return {"message": "Email successfully verified"}

@app.post("/users/", response_model=schemas.UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user.

    Args:
        user (schemas.UserCreate): The user data for creating a new user.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.

    Raises:
        HTTPException: If the email is already registered.

    Returns:
        The created user model.
    """

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token.

    Args:
        form_data (OAuth2PasswordRequestForm, optional): The user's login credentials.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.

    Raises:
        HTTPException: If authentication fails.

    Returns:
        A token response model with the access token and token type.
    """

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/contacts/", response_model=schemas.Contact)
@limiter.limit("5/minute")
def create_contact(request: Request, contact: schemas.ContactCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Creates a new contact for the current user.

    This endpoint is rate-limited to 5 requests per minute.

    Args:
        request (Request): The request object.
        contact (schemas.ContactCreate): The contact data for creating a new contact.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.
        current_user (models.User, optional): Dependency that retrieves the currently authenticated user.

    Returns:
        The created contact model.
    """

    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)


@app.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Retrieves a list of contacts for the current user.

    Args:
        skip (int, optional): The number of items to skip (for pagination).
        limit (int, optional): The maximum number of items to return (for pagination).
        db (Session, optional): Dependency that provides a SQLAlchemy Session.
        current_user (models.User, optional): Dependency that retrieves the currently authenticated user.

    Returns:
        A list of contact models belonging to the current user.
    """

    contacts = crud.get_user_contacts(db, user_id=current_user.id, skip=skip, limit=limit)
    return contacts


@app.get("/contacts/{contact_id}", response_model=Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves a single contact by ID for the current user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.
        current_user (models.User, optional): Dependency that retrieves the currently authenticated user.

    Raises:
        HTTPException: If the contact is not found or does not belong to the current user.

    Returns:
        The requested contact model.
    """

    db_contact = crud.get_contact(db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Updates a contact for the current user.

    Args:
        contact_id (int): The ID of the contact to update.
        contact (schemas.ContactUpdate): The updated contact data.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.
        current_user (models.User, optional): Dependency that retrieves the currently authenticated user.

    Returns:
        The updated contact model.
    """

    return crud.update_contact(db=db, contact_id=contact_id, contact=contact, user_id=current_user.id)


@app.delete("/contacts/{contact_id}", response_model=Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Deletes a contact for the current user.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (Session, optional): Dependency that provides a SQLAlchemy Session.
        current_user (models.User, optional): Dependency that retrieves the currently authenticated user.

    Returns:
        The deleted contact model, if found and deleted successfully.
    """

    return crud.delete_contact(db=db, contact_id=contact_id, user_id=current_user.id)


@app.get("/contacts/upcoming_birthdays/")
def get_upcoming_birthdays(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves contacts with upcoming birthdays within the next 7 days for the current user.

    Args:
        db (Session, optional): Dependency that provides a SQLAlchemy Session.
        current_user (models.User, optional): Dependency that retrieves the currently authenticated user.

    Returns:
        A list of contact models with upcoming birthdays.
    """

    return crud.get_upcoming_birthdays(db, user_id=current_user.id)
