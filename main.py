import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from generator import create_dxf, create_obj

app = FastAPI(title="Al-Qannas Landscape API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel Serverless Functions have a read-only filesystem except for /tmp
UPLOAD_DIR = "/tmp/uploads" if os.getenv("VERCEL") else "uploads"
OUTPUT_DIR = "/tmp/outputs" if os.getenv("VERCEL") else "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/process")
async def process_landscape(
    image: UploadFile = File(...),
    width: float = Form(...),
    length: float = Form(...)
):
    # Save uploaded image
    image_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Generate files
    base_name = os.path.splitext(image.filename)[0]
    dxf_path = os.path.join(OUTPUT_DIR, f"{base_name}_plan.dxf")
    obj_path = os.path.join(OUTPUT_DIR, f"{base_name}_3d.obj")
    
    create_dxf(dxf_path, width, length)
    create_obj(obj_path, width, length)
    
    return {
        "message": "Files generated successfully",
        "dxf_url": f"/api/download/{base_name}_plan.dxf",
        "obj_url": f"/api/download/{base_name}_3d.obj"
    }

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    return {"error": "File not found"}
