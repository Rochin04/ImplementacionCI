from fastapi import FastAPI, HTTPException, Response, Depends
from datetime import datetime, timezone
from typing import Any
from contextlib import asynccontextmanager
from typing import Annotated, Generic, TypeVar
from pydantic import BaseModel
from sqlmodel import create_engine, SQLModel, Session, select, Field

class Campaing(SQLModel, table=True):
    campaing_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc),nullable=True, index=True)

class CampaingCreate(SQLModel):
    name: str
    due_date: datetime | None = None

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread":False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaing)).first():
            session.add_all([
                    Campaing(name="summer lunch", due_date=datetime.now()),
                    Campaing(name="Black Friday", due_date=datetime.now())
                ])
            session.commit()
    yield

#app = FastAPI(root_path="/api/v1", lifespan=lifespan)
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World!"}

T = TypeVar("T")
class Respons(BaseModel, Generic[T]):
    data: T
@app.get("/campaings", response_model=Respons[list[Campaing]])
async def read_campaings(session: SessionDep):
    data = session.exec(select(Campaing)).all()
    return {"data": data}

@app.get("/campaings/{id}", response_model=Respons[Campaing])
async def read_campaing(id: int, session: SessionDep):
    data = session.get(Campaing, id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data":data}

@app.post("/campaings", status_code=201, response_model=Respons[Campaing])
async def create_campaings(campaing:CampaingCreate, session:SessionDep):
    db_campaing = Campaing.model_validate(campaing)
    session.add(db_campaing)
    session.commit()
    session.refresh(db_campaing)
    return {"data": db_campaing}

@app.put("/campaings{id}", response_model=Respons[Campaing])
async def update_campaing(id: int, campaing: CampaingCreate, session: SessionDep):
    data = session.get(Campaing, id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = campaing.name
    data.due_date = campaing.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}

@app.delete("/campaings/{id}",status_code=204)
async def delete_campaing(id: int, session: SessionDep):
    data = session.get(Campaing, id)
    if not data:
        raise HTTPException(status_cod=404)
    session.delete(data)
    session.commit()
    return {"message": "Campaing deleted"} 
