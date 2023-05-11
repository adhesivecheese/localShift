from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database.database import Session, engine
import database.crud as crud
import database.models as models
import database.schemas as schemas

models.Base.metadata.create_all(bind=engine)
iface = crud.ReadOnlyInterface()

app = FastAPI()

origins = ["*"]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

def get_db():
	db = Session()
	try:
		yield db
	finally:
		db.close()

@app.get("/api")
def root():
	return {"message": "It Works!"}

@app.get("/api/v0/post/{id}", response_model=schemas.Post)
def read_post(id: str, db: Session = Depends(get_db)):
	db_post = iface.read_post(db, id=id)
	if db_post is None: raise HTTPException(status_code=404, detail="Post not found")
	return db_post

@app.get("/api/v0/comment/{id}", response_model=schemas.Comment)
def read_post(id: str, db: Session = Depends(get_db)):
	db_comment = iface.read_comment(db, id=id)
	if db_comment is None: raise HTTPException(status_code=404, detail="Comment not found")
	return db_comment