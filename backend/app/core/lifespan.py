from contextlib import asynccontextmanager
from fastapi import FastAPI
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup LOGIC
    from app.services.rag_service import rag_service
    
    # Ensure path is absolute and correct relative to current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming app is in backend/app, so core is backend/app/core
    # experience.csv is in backend/app/data
    csv_path = os.path.join(os.path.dirname(current_dir), "data", "experience.csv")
    
    print(f"INFO: Lifecycle startup - Checking for experience data at {csv_path}...")
    try:
        rag_service.index_csv(csv_path)
    except Exception as e:
        print(f"ERROR: Lifecycle failed to index CSV on startup: {e}")
        
    yield
    
    # Shutdown LOGIC
    print("INFO: Lifecycle shutdown - Cleaning up resources...")
