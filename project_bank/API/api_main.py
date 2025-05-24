#Huvudentrypoint till API
from Pipeline.database import engine, Base, SessionLocal
from Models import account, customer, transaction
from fastapi import FastAPI

app = FastAPI(title="BankAPI")

@app.get("/")
def read_root():
    return {"message": "Välkommen till bankens API"}

# Startar init av databasen
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()