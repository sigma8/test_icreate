from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from .schemas import TodoItem, TodoPayload, UserPayload
from . import models, database, utils
from sqlalchemy.orm import Session
from app.oauth2 import *

router = APIRouter()

@router.post("/users/")
def create_user(payload: UserPayload, db: Session = Depends(database.get_db)):
    passhash = utils.password_hash(payload.password)
    payload.password = passhash
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users/{id}") 
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail=f"No se pudieron validar las credenciales", 
                                        headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user



@router.get("/items/", response_model=List[TodoItem])
def get_items(db: Session = Depends(database.get_db)):
    items = db.query(models.Item).group_by(models.Item.title).all()
    return items

@router.get("/items/{id}", response_model=TodoItem)
def get_item(id: int, db: Session = Depends(database.get_db)):
    item = db.query(models.Item).group_by(models.Item.id).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                            detail=f"Item {id} no fue encontrado")
    return item


@router.post("/items/", response_model=TodoItem,status_code=status.HTTP_201_CREATED,
    response_description="The item has been created successfully.")
def create_item(payload: TodoPayload, db: Session = Depends(database.get_db), current_user: int = get_current_user):
    new_post = models.Item(user_id=current_user.id, **payload.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

    """Add an item to the store."""

    # TODO: Implement this.
    # Requirements:
    # * Ensure an user is authenticated with basic credentials.
    # * Add the username to the item.


@router.put("/items/{id}", response_model=TodoItem)
def update_item(id: int, payload: TodoPayload, db: Session = Depends(database.get_db), current_user: int = get_current_user):
    item_query = db.query(models.Item).filter(models.Item.id == id)
    item_update = item_query.first()
    if item_update == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                            detail=f"item {id} no fue encontrado")
    if item_update.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="No esta autorizado para realizar esta accion")
    item_query.update(payload.dict(), synchronize_session=False)
    db.commit()
    return item_query.first()
 
    # TODO: Implement this.
    # * Ensure the user is authenticated. If not, either return a 401 response
    #   or raise an `HttpException` with a 401 code.
    # * Ensure that the item is stored already in the datastore. If not, raise
    #   an `HttpException` with a 404 code or return a 404 response.
    # * Check the username matches the item's username. If not, return a 403
    #   response or raise a `HttpException` with a 403 code.
    # * Apply the update and save it to the database.


@router.delete("/items/{id}", response_class=Response, status_code=204)
def remove_item(id: int,db: Session = Depends(database.get_db), current_user: int = get_current_user):
    item_query = db.query(models.Item).filter(models.Item.id == id)
    item = item_query.first()
    if item == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                            detail=f"item {id} no fue encontrado")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="No esta autorizado para realizar esta accion")
    item_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    # TODO: Implement this
    # 1. Check that the item exists in the datastore.
    # 2. Ensure the user is authenticated.
    # 3. Check if the currently logged username matches.
    # 4. Remove the item from the store

