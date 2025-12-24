from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Import cái này
# --- API Router ---
from src.api import router as api_router

# --- Database ---
from src.core.database import create_db_tables

app = FastAPI(title="JiraMeet API")

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
    return {"message": "JiraMeet AI Backend is operational! Visit /docs for API documentation."}


# --- Startup Event (Create DB Tables) ---
@app.on_event("startup")
def on_startup():
    print("Attempting to create database tables...")
    try:
        create_db_tables()
        print("Database tables created successfully or already exist.")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")


# --- Run server locally ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
