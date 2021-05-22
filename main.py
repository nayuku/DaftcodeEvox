import sqlite3
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("./api.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()

@app.get("/")
async def root():
    app.db_connection.row_factory = sqlite3.Row
    user = app.db_connection.execute("SELECT * FROM users WHERE id=1;").fetchone()
    return user


