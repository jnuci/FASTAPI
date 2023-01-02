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
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}
    # title str, content str

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    # we use 'id: int' to validate id can be an int
    post = find_post(id)
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
    # deleting post
    # find the index in array
    # my_posts.pop(id)
    # don't send data back with a 204
    index = post_index(id)

    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist.")

    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = post_index(id)
    
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exisst.")

    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict

    return {"data": post_dict}
