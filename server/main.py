from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# --- API Router ---
from src.api import router as api_router

# --- Database ---
from src.core.database import create_db_tables


# --- Lifespan (replaces deprecated @app.on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Attempting to create database tables...")
    try:
        create_db_tables()
        print("Database tables created successfully or already exist.")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
    yield  # Application runs here


app = FastAPI(title="ProMeet API", lifespan=lifespan)

# --- CORS ---
origins = [
    # Frontend (React)
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://[::1]:3000",          # IPv6 localhost

    # Meeting Analysis Agent
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Include API Routers ---
app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Health Check ---
@app.get("/", tags=["Health Check"])
def root():
    return {"message": "ProMeet API is operational! Visit /docs for API documentation."}


# --- Run server locally ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
