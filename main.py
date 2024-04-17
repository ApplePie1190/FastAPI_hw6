from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from databases import Database
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr


DATABASE_URL = "sqlite:///mydatabase.db"

database = Database(DATABASE_URL)
metadata = MetaData()
app = FastAPI()


users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String()),
    Column("surname", String()),
    Column("birthday", String()),
    Column("email", String()),
    Column("address", String()),
)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


class UserIn(BaseModel):
    name: str = Field(..., min_length=2)
    surname: str = Field(..., min_length=2)
    birthday: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    email: EmailStr = Field(..., max_length=128)
    address: str = Field(..., min_length=5)


class User(BaseModel):
    id: int
    name: str = Field(..., min_length=2)
    surname: str = Field(..., min_length=2)
    birthday: str = Field(pattern=r"\d{4}-\d{2}-\d{2}")
    email: EmailStr = Field(..., max_length=128)
    address: str = Field(..., min_length=5)


@app.post("/users/", response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(
        name=user.name, 
        surname=user.surname, 
        birthday=user.birthday,
        email=user.email,
        address=user.address
        )
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.get("/users/", response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted'}