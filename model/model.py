
from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, DateTime, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

Base = declarative_base()

#Model for User

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    offers = relationship("Offer", back_populates="owner")


class UserValidater(User):
    def user_validate(details, db):
        result = db.query(User).filter(User.email == details["email"]).first()
        return result


#Model For Offer Type

class OfferType(Base):
    __tablename__ = "offer_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    offers = relationship("Offer", back_populates="type")



#Model For Offer

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey('offer_types.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Integer)
    off_persentage = Column(Integer, nullable=True)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)

    type = relationship("OfferType", back_populates="offers")
    owner = relationship("User", back_populates="offers")
