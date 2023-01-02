from fastapi import FastAPI, Body, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
# uvicorn main:app --reload

app = FastAPI()

# using the Post class with BaseModel allows us to check
# for each entry we want or give default values

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
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



# each post represented as dictionary nested in list
my_posts = [{"title": "title of post1", "content": "content of post1", "id": 1},
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p["id"] == int(id):
            return p
def post_index(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """), (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}
    # title str, content str

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    post = cursor.fetchone()
    # we use 'id: int' to validate id can be an int
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} does not exist. Sorry pal.")
        # can also use
        # response.status_code = 404
        # return {"post_detail": f"Post with id {id} does not exist. Sorry :( ."}
    return {"post_detail": post} 

'''
Create: Post
Read: Get
Update: Put/Patch, put submits all the info again.
        Patch will change only what you submit
Delete: Delete
'''

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()

    # deleting post
    # find the index in array
    # my_posts.pop(id)
    # don't send data back with a 204

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s  WHERE id = %s RETURNING * """, (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exisst.")

    return {"data": updated_post}
