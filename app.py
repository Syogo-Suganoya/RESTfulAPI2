from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# DB設定（SQLite or PostgreSQL）
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./db.sqlite3")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# モデル定義
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)


# Pydanticスキーマ
class TodoSchema(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        orm_mode = True


class TodoCreate(BaseModel):
    title: str
    done: bool = False


class TodoUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# FastAPIインスタンス
app = FastAPI()


# DB初期化＆シードデータ
def init_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.query(Todo).first():
            initial_data = [
                Todo(title="買い物に行く"),
                Todo(title="読書をする"),
                Todo(title="コードを書く", done=True)
            ]
            db.add_all(initial_data)
            db.commit()
            print("✅ 初期データを挿入しました")


init_db()


# DI（依存性注入）用
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ルーティング
@app.get("/todos", response_model=List[TodoSchema])
def get_todos(db: Session = next(get_db())):
    return db.query(Todo).all()


@app.get("/todos/{todo_id}", response_model=TodoSchema)
def get_todo(todo_id: int, db: Session = next(get_db())):
    todo = db.query(Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=TodoSchema, status_code=201)
def create_todo(todo: TodoCreate, db: Session = next(get_db())):
    new_todo = Todo(title=todo.title, done=todo.done)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@app.put("/todos/{todo_id}", response_model=TodoSchema)
def update_todo(todo_id: int, updates: TodoUpdate, db: Session = next(get_db())):
    todo = db.query(Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if updates.title is not None:
        todo.title = updates.title
    if updates.done is not None:
        todo.done = updates.done
    db.commit()
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = next(get_db())):
    todo = db.query(Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
