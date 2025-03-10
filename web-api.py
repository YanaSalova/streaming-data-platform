from fastapi import FastAPI, HTTPException
import psycopg2
import os
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mylabdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "mysecretpassword")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


class UserCreate(BaseModel):
    name: str
    country: str


@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, country, created_at FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": row[0],
            "name": row[1],
            "country": row[2],
            "created_at": row[3].isoformat() if row[3] else None
        }
    finally:
        cur.close()
        conn.close()


@app.post("/users")
def create_user(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, country) VALUES (%s, %s) RETURNING id, created_at",
            (user.name, user.country)
        )
        inserted_row = cur.fetchone()
        new_id = inserted_row[0]
        created_at = inserted_row[1]
        conn.commit()
        return {
            "id": new_id,
            "name": user.name,
            "country": user.country,
            "created_at": created_at.isoformat()
        }
    finally:
        cur.close()
        conn.close()
