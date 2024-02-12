# файл models.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    Represents a user within the database.

    Attributes:
        id (int): Unique identifier for the user, serves as the primary key.
        email (str): Unique email address of the user, also indexed for fast lookup.
        hashed_password (str): Hashed password for the user.
        is_active (bool): Flag to indicate if the user's account is active.
        is_verified (bool): Flag to indicate if the user's email has been verified.
        verification_code (str): Code sent to the user for verifying their email address.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String, unique=True, nullable=True)  # Изменено с verification_token на verification_code


class Contact(Base):
    """
    Represents a contact associated with a user in the database.

    Attributes:
        id (int): Unique identifier for the contact, serves as the primary key.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Unique email address of the contact.
        phone_number (str): Phone number of the contact.
        birthday (Date): Birthday of the contact.
        additional_info (str): Additional information about the contact.
        owner_id (int): Identifier of the user who owns this contact, foreign key to the users table.
        owner (relationship): SQLAlchemy relationship linking to the User who owns this contact.
    """

    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birthday = Column(Date)
    additional_info = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))  # Исправлено с 'user.id' на 'users.id'
    owner = relationship("User")


DATABASE_URL = "postgresql://alex:123456789@db/dbalex"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency that produces a new SQLAlchemy session from the session factory (SessionLocal).
    This is to be used with FastAPI's Depends to provide a session for each request.

    Yields:
        A session scoped to the context of the function it is used in.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()