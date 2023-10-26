from calendar import c
from enum import auto
from logging import raiseExceptions
from multiprocessing import synchronize
from os import close
from pickle import NONE
from sqlite3 import Cursor
from time import sleep
from typing import Optional, List
from typing_extensions import deprecated
from fastapi import FastAPI, Response, status, HTTPException , Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from sqlalchemy import false
from . import models, schemas, utils

from sqlalchemy.orm import Session
from .database import get_db, engine 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()





while True: 
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',user='postgres',
                                password='admin', cursor_factory=RealDictCursor)
        
        cursor=conn.cursor()

        print("Database connection was successfull!")
        break

    except Exception as error:
        print("Database connection is Failed")

        print("Error :",error)

        time.sleep(2)




@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/posts", response_model=List[schemas.Post])
def get_post():
    cursor.execute("""select * from post""")
    posts=cursor.fetchall()
    print(posts)
    return posts



@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def creat_post(post:schemas.CreatePost, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO post (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title,post.content, post.published))
    # new_post=cursor.fetchone()
    # conn.commit()
     
    # create post using SQLAlchemy
     
    new_post=models.Post(**post.dict())

    # new_post=models.Post(title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post



@app.get("/posts/{id}",response_model=schemas.Post)
def get_post(id:int, db: Session = Depends(get_db)):

    # cursor.execute("""select * from post where id= %s  """,(str(id),))
    # post=cursor.fetchone()

    post= db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"post with id: {id} not found" )

    return post



@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db)):

    # cursor.execute("""delete from post where id= %s  returning *""",(str(id),))
    # deleted_post=cursor.fetchone()
    # conn.commit()

    post= db.query(models.Post).filter(models.Post.id == id)

    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} not exist")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}",response_model=schemas.Post)
def update_post(id: int , updated_post:schemas.CreatePost, db: Session = Depends(get_db)):

    # cursor.execute(""" update post set title = %s, content= %s, published= %s where id = %s RETURNING * """,
    #                (post.title,post.content, post.published, str(id)))
    
    # updated_post=cursor.fetchone()
    # conn.commit()

    post_query= db.query(models.Post).filter(models.Post.id == id)
    post=post_query.first()

    if post==None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} not exist")

    post_query.update(updated_post.dict(), synchronize_session=False)    
    db.commit()
    return post_query.first()




@app.get("/sqlalchemy")
def test_post(db: Session = Depends(get_db)):

    post= db.query(models.Post).all()
    return post


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate, db: Session = Depends(get_db)):

    # Hash the password user.password

    hash_password=utils.hash(user.password)
    user.password=hash_password 

    new_user=models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



@app.get("/users/{id}",response_model=schemas.UserOut)
def get_user(id:int, db: Session = Depends(get_db)):

    user= db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"post with id: {id} not found" )

    return user

