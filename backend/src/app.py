from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import importlib.util
import sys
from typing import List, Optional

from core.dependencies import get_current_user
from apis.auth import auth_router
from init_db import init_database


app = FastAPI(
    title="Housekeeping System",
    description="Hotel Housekeeping Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def include_routers_from_folder(folder: str = "api"):
    routers_path = Path(__file__).parent / folder
    if not routers_path.is_dir():
        print(f"Warning: router folder not found: {routers_path}")
        return

    for file_path in routers_path.glob("*.py"):
        if file_path.name == "__init__.py" or file_path.name == "auth.py":
            continue

        module_name = f"app.{folder}.{file_path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, "router"):
            router = getattr(module, "router")
            app.include_router(router, dependencies=[Depends(get_current_user)])
        
        if hasattr(module, "public_router"):
            app.include_router(module.public_router)


app.include_router(auth_router)
include_routers_from_folder("apis")

@app.get("/health")
async def root():
    return {"message": "Welcome to Housekeeping Management System"}

@app.on_event("startup")
def startup_event():
    init_database("mysql")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
