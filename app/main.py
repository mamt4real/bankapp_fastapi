from fastapi import FastAPI
from .routers import customers,  auth, accounts, transactions, views
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# import jinja2

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

template = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
# database connection
# models.Base.metadata.create_all(bind=engine)



app.include_router(views.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
