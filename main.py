import sqlite3
import uuid
import hashlib
from fastapi import FastAPI, Response, status, HTTPException, Cookie, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from pydantic import BaseModel

app = FastAPI()
app.session_tokens = []

security = HTTPBasic()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("./api.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.post("/auth", status_code=status.HTTP_201_CREATED)
async def auth(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    login = credentials.username
    hash = hashlib.sha256(credentials.password.encode("utf-8")).hexdigest()

    app.db_connection.row_factory = sqlite3.Row
    dbuser = app.db_connection.execute("SELECT login, hash from users"
                                       " where login = :login and hash = :hash",
                                       {"login": login, "hash": hash}).fetchone()
    if dbuser is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if login == dbuser[0] and hash == dbuser[1]:
        session_token = str(uuid.uuid1())
        app.session_tokens.append(session_token)
        response.set_cookie(key="session_token", value=session_token)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"detail": "Authorized"}


@app.get("/read_msg/{id}")
async def read_msg(id: int):
    app.db_connection.row_factory = sqlite3.Row
    counter = app.db_connection.execute("SELECT counter FROM messages WHERE id = :id", {'id': id}).fetchone()
    if counter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    app.db_connection.execute("UPDATE messages SET counter = :counter WHERE id = :id;",
                              {'counter': counter[0] + 1, "id": id})
    app.db_connection.commit()

    msg = app.db_connection.execute(
        "SELECT text, counter FROM messages WHERE id = :id",
        {'id': id}).fetchone()
    return msg


class Message(BaseModel):
    text: str


@app.post("/add_msg", status_code=status.HTTP_201_CREATED)
async def add_msg(msg: Message, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if len(msg.text.strip()) == 0 or len(msg.text) > 160:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Wrong message length (proper: 1-160 chars)")

    app.db_connection.row_factory = sqlite3.Row
    cursor = app.db_connection.execute("INSERT INTO messages (text, counter) VALUES (:text, 0)",
                                       {"text": msg.text})
    app.db_connection.commit()

    last_id = cursor.lastrowid
    return {"detail": f"Created message with {last_id}"}


@app.delete("/delete_msg/{id}")
async def delete_msg(id: int, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute("SELECT * FROM messages WHERE id = :id", {'id': id}).fetchone()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    app.db_connection.execute("DELETE FROM messages WHERE id = :id;", {'id': id})
    app.db_connection.commit()
    return {"detail": f"Message with {id=} deleted"}


@app.put("/edit_msg/{id}")
async def edit_msg(id: int, msg: Message, session_token: str = Cookie(None)):
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if len(msg.text.strip()) == 0 or len(msg.text) > 160:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Wrong message length (proper: 1-160 chars)")

    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute("SELECT * FROM messages WHERE id = :id", {'id': id}).fetchone()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    app.db_connection.execute("UPDATE messages SET text = :text, counter = 0 WHERE id = :id;",
                              {'text': msg.text, "id": id})
    app.db_connection.commit()

    return {"detail": f"Message with {id=} altered with new text"}
