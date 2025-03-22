from fastapi import FastAPI, HTTPException
import psycopg2
import os
from pydantic import BaseModel
from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()


DB_HOST = os.getenv("DB_HOST", "postgres_db")
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


aggregated_data = []

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
        
        new_user = {
            "id": new_id,
            "name": user.name,
            "country": user.country,
            "created_at": created_at.isoformat()
        }
     
        aggregated_data.append(new_user)
        
        return new_user
    finally:
        cur.close()
        conn.close()

def flush_aggregated_data():
    global aggregated_data
    if aggregated_data:
        os.makedirs("./data", exist_ok=True)
        filename = f"./data/aggregated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(aggregated_data, f, ensure_ascii=False, indent=4)
        print(f"Данные выгружены в файл: {filename}")
        aggregated_data = [] 
    else:
        print("Буфер пуст, нечего выгружать.")


scheduler = BackgroundScheduler()
scheduler.add_job(flush_aggregated_data, 'interval', seconds=60)

@app.on_event("startup")
def startup_event():
    scheduler.start()
    print("Scheduler запущен")

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    print("Scheduler остановлен")
