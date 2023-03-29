from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db


# uvicorn main:app --reload

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# using the Post class with BaseModel allows us to check
# for each entry we want or give default values

while True:
    try:
        conn = psycopg2.connect(host='localhost',
        database='fastAPI',
        user='postgres',
        password='UC$b2019?!', cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print("Connection to database failed")
        print(f"Error was {error}")
        time.sleep(2) 

@app.get("/")
def root():
    return {"message": "Hello World"} 

@app.get("/posts", response_model = list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model = schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute(("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """),
    # (post.title, post.content, post.published))

    # new_post = cursor.fetchone()
    # conn.commit()

    # new_post = models.Post(title=post.title, content=post.content, published=post.published) 
    new_post = models.Post(**post.dict())

    db.add(new_post)
    db.commit()
    # .refresh in order to return the created post
    db.refresh(new_post)

    return new_post
    # title str, content str

@app.get("/posts/{id}", response_model = schemas.Post)
def get_post(id: int,  db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    # # we use 'id: int' to validate id can be an int
    post = db.query(models.Post).filter(models.Post.id == id).first()
    

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exist. Sorry pal.")
        # can also use
        # response.status_code = 404
        # return {"post_detail": f"Post with id {id} does not exist. Sorry :( ."}
    return post

'''
Create: Post
Read: Get
Update: Put/Patch, put submits all the info again.
        Patch will change only what you submit
Delete: Delete
'''

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    # # deleting post
    # # find the index in array
    # # my_posts.pop(id)
    # # don't send data back with a 204

    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist.")
    else:
        post_query.delete(synchronize_session = False)
        db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model = schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING * """, (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit()
    

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exist.")
    
    post_query.update(updated_post.dict(), synchronize_session=False)

    db.commit()

    return post_query.first() 

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model = schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password



    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users/{id}", response_model = schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    pass
