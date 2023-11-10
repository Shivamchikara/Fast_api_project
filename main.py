
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


from model.model import Base, User, UserValidater, Offer, OfferType
from crud.crud import get_user, get_user_by_username, create_user, AuthHandler, get_offers_filter
from crud.crud import create_offer, get_offer_types, create_offer_types, update_offer_type
import uvicorn

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

#Data Base Handler

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


auth_handler = AuthHandler()

#User Register by post data in JSON file through Postman

@app.post("/register")
def register(detail: dict, db: Session = Depends(get_db)):
    # Check if user already exists

    detail["password"] = auth_handler.get_password_hash(detail["password"])

    if get_user_by_username(db, detail["username"]):
        raise HTTPException(status_code=400, detail="Username already registered")

    return create_user(db=db, details=detail)

#Get User by User_ID

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#User Login with access token and refresh token

@app.post("/login")
def login(details: dict, db: Session = Depends(get_db)):
    is_valid = UserValidater.user_validate(details, db)
    print(is_valid)
    if is_valid:
        hash_pwd = is_valid.password
        if auth_handler.verify_password(details["password"], hash_pwd):
            token = {"access_token": auth_handler.access_encode_token(details["email"]),
                     "refresh_token": auth_handler.refresh_encode_token(details["email"])
                     }
            return {"tokens": token}
        else:
            return {"message": "password is not valid"}
    else:
        return HTTPException(status_code=404, detail="User not found")


#Create Offers Using by JSON

@app.post("/offers")
def create_offer_route(details:dict, db: Session = Depends(get_db)):
    return create_offer(db=db, offer_type_id=details["offer_type_id"], owner_id=details["owner_id"], amount=details["amount"], off_percentage=details.get("off_percentage", 0), start_date=details["start_date"], end_date=details["end_date"])

#Offers filter by Details like (date, Owner_ID, Offer_ID etc.)

@app.get("/offers_filter/")
def get_offers_endpoint(

    details:dict,
    db: Session = Depends(get_db)
):
    print(details)
    return get_offers_filter(db=db, details=details)



#Create offertypes Using by JSON file

@app.post("/offer_types")
def create_offer_types_routs(
        details:dict, db: Session = Depends(get_db)):
    return create_offer_types(db=db, name=details["name"])

#Get all Offers Type

@app.get("/offer_types")
def list_offer_types(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_offer_types(db, skip, limit)

#Get Offer Type Using by Offer type ID

@app.get("/offer_types/{offer_type_id}")
def get_offer_type(offer_type_id: int, db: Session = Depends(get_db)):
    offer_type = db.query(OfferType).filter(OfferType.id == offer_type_id).first()
    if offer_type is None:
        raise HTTPException(status_code=404, detail="Offer Type not found")
    return offer_type

#Update Offer Type Using By Offer Type ID

@app.put("/offer_types/{offer_type_id}")
def update_offer_type_route(details:dict, db: Session = Depends(get_db)):
    updated_offer_type = update_offer_type(db, details["offer_type_id"], details["new_name"])
    if updated_offer_type:
        return updated_offer_type
    else:
        raise HTTPException(status_code=404, detail="Offer Type not found")



#Get all Offers

@app.get("/offers/")
def get_offers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Offer).offset(skip).limit(limit).all()

#Get Offers Using By Offer ID

@app.get("/offers/{offer_id}")
def get_offer(offer_id: int, db: Session = Depends(get_db)):
    return db.query(Offer).filter(Offer.id == offer_id).first()



#Delete Offers using by odder ID

@app.delete("/offers/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    db.delete(offer)
    db.commit()
    return {"message": "Offer deleted successfully"}






if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
