from typing import List
from webbrowser import get
from fastapi import APIRouter, Response
from .schemas import TodoItem, TodoPayload, UserPayload #,User

#-----Agregado jtortolero-----
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from .models import Item, User
from .utils import password_hash
from .oauth2 import *
#-----------------------------


router = APIRouter()


@router.get("/items/", response_model=List[TodoItem])
def get_items(db:Session=Depends(get_db)):
    """Retrieve a persistent list of items."""
    # TODO: Implement this
    items = db.query(Item).filter(Item.title).all()
    return items


@router.get("/items/{id}", response_model=TodoItem)
def get_item(id: int, db:Session=Depends(get_db)):
    """Retrieve a particular item from the store."""
    # TODO: Implement this.
    item = db.query(Item).filter(Item.id==id).first()
    if not item:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
        detail=f'Item con id={id} no existe')
    return item
    

@router.post(
    path="/items/",
    response_model=TodoItem,
    status_code=201,
    response_description="The item has been created successfully.",
)
def create_item(payload: TodoPayload, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    """Add an item to the store."""
    # TODO: Implement this.
    # Requirements:
    # * Ensure an user is authenticated with basic credentials.
    # * Add the username to the item.
    new_item = Item(user_id=current_user.id, **Item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item



@router.put("/items/{id}", response_model=TodoItem)
def update_item(id: int, payload: TodoPayload, db:Session=Depends(get_db), 
                current_user: User=Depends(get_current_user)):
    # TODO: Implement this.
    # * Ensure the user is authenticated. If not, either return a 401 response
    #   or raise an `HttpException` with a 401 code.
    # * Ensure that the item is stored already in the datastore. If not, raise
    #   an `HttpException` with a 404 code or return a 404 response.
    # * Check the username matches the item's username. If not, return a 403
    #   response or raise a `HttpException` with a 403 code.
    # * Apply the update and save it to the database.
    item_query = db.query(Item).filter(Item.id == id)
    item_update = item_query.first()
    if item_update == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                            detail=f"post {id} no fue encontrado")
    if item_update.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="No esta autorizado para realizar esta accion")
    item_query.update(payload.dict(), synchronize_session=False)
    db.commit()
    return item_query.first()


@router.delete("/items/{id}", response_class=Response, status_code=204)
def remove_item(id: int, db:Session=Depends(get_db), current_user: int= Depends(get_current_user)):
    # TODO: Implement this
    # 1. Check that the item exists in the datastore.
    # 2. Ensure the user is authenticated.
    # 3. Check if the currently logged username matches.
    # 4. Remove the item from the store.
    item_query = db.query(Item).filter(Item.id == id)
    item = item_query.first()
    if item == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                            detail=f"Item {id} no fue encontrado")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="No esta autorizado para realizar esta accion")
    item_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/")
def create_user(payload: UserPayload, db:Session=Depends(get_db)):
    # TODO: Implement this.
    # 1. Validate the username has no uppercase letter, @ sign, nor
    #   punctuations.
    # 2. Hash the password and store the user in the data store.
    user = User(
        name = payload.name,
        username = payload.username,
        email = payload.email,
        password = password_hash(payload.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# TODO: Document this endpoint
@router.get("/users/me")
def get_current_user():
    user = get_current_user
    return user

