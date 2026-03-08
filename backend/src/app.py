from pathlib import Path
import importlib.util
import sys
from typing import List, Optional


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from core.dependencies import get_current_user
from apis.auth import auth_router
from apis.portal import router as portal_router
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
    """Dynamically include routers from a specified folder."""
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
app.include_router(portal_router)
include_routers_from_folder("apis")

@app.get("/health")
async def root():
    """"Health check endpoint to verify that the application is running."""
    return {"message": "<p style='color:blue;'>Welcome to Housekeeping Management System</p>"}

@app.on_event("startup")
def startup_event():
    """"Initialize the database connection on application startup."""
    init_database("mysql")


# @app.get("/pic/{id}")
# def output_pic(id: int):
#     """Test endpoint to verify that static files are served correctly."""
#     img_path = Path(__file__).parent / "static" / f"{id}.jpg"
#     print(f"Attempting to serve image from: {img_path}")
#     if not img_path.is_file():
#         raise HTTPException(status_code=404, detail="Image not found")

#     return FileResponse(img_path, media_type="image/jpeg")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
