import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from model.model import User, Offer, OfferType




#Offer Create and Data send by JSON Using Postman

def create_offer(db: Session, offer_type_id: int, owner_id: int, amount: int, off_percentage, start_date, end_date):
    start_date1 = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date1 = datetime.strptime(end_date, '%Y-%m-%d').date()

    offer = Offer(type_id=offer_type_id, owner_id=owner_id, amount=amount, off_persentage=off_percentage, start_date=start_date1, end_date=end_date1)
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


#Offers Filter through different different parameter like (date, user, offer)

def get_offers_filter(db: Session, details:dict):


    filter_by = details.get("filter_by")
    val = db.query(Offer)
    try:
        order_column = getattr(Offer, filter_by)
        print(order_column)
        order_func = asc if details.get("asc", 1) else desc
        val = val.order_by(order_func(order_column)).all()
        return val
    except:
        return {"message": "Invalid Column name"}, 400



#Get user through user ID

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()



def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first() # SELECT * FROM users WHERE username=username

#User details for create user database
def create_user(details: dict, db: Session):

    db_user = User(username=details["username"], email=details["email"], password=details["password"])
    db.add(db_user)
    print(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = "SivamSec@#1"

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def access_encode_token(self, user_id):
        payload = {
            "exp": datetime.utcnow()+timedelta(days=2, minutes=5),
            "iat": datetime.utcnow(),
            "sub": user_id,
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm="HS256"
        )
    def refresh_encode_token(self, user_id):
        payload = {
            "exp": datetime.utcnow()+timedelta(days=10),
            "iat": datetime.utcnow(),
            "sub": user_id,
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm="HS256"
        )



    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="signature has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail="Invalid Token")

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        # print(auth.credentials)
        return self.decode_token(auth.credentials)



#Offer Type Detaile

def get_offer_types(db: Session, skip: int = 0, limit: int = 10):
    return db.query(OfferType).offset(skip).limit(limit).all()

def create_offer_types(db: Session, name: str):
    db_offer_types = OfferType(name=name)
    db.add(db_offer_types)
    print(db_offer_types)
    db.commit()
    db.refresh(db_offer_types)
    return db_offer_types



def update_offer_type(db: Session, offer_type_id: int, new_name: str):
    offer_type_change = db.query(OfferType).filter(OfferType.id == offer_type_id).first()
    if offer_type_change:
        offer_type_change.name = new_name
        db.commit()
        db.refresh(offer_type_change)
        return offer_type_change
    return None

# Offer Details

def get_offers(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Offer).offset(skip).limit(limit).all()


def delete_offer(db: Session, offer_id: int):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    db.delete(offer)
    db.commit()
    return {"message": "Offer deleted successfully"}


