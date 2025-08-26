from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from app.models import load_trained_model, predict

app = FastAPI(
    title= "Cat vs Dog image classfier API",
    description= "Image classification",
    version= "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

model = None
class_names = ["cats","dogs"]

@app.on_event("startup")
async def startup_event():
    global model
    model_path = "models/cats_dogs_model.pth"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    try:
        model = load_trained_model(model_path)
        print("Model loaded successfully")

    except Exception as e:
        print(f"Error loading model:{e}")
        raise e
    
@app.get("/")
async def root():
    return {"message":"Resnet18 Image Classification API is running"}

@app.get("/health")
async def health_check():
    return{
        "status": "healthy 😊",
        "model_loaded": model is not None,
        "num_classes": 2
    } 

@app.post("/predict")
async def predictImage(file:UploadFile = File(...)):
    global model
    if model is None:
        raise HTTPException(status_code=500, detail="Model Not Loaded")   
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400,detail= "File must be an image")

    try:

        image_byte = await file.read()

        result = predict(model, image_byte, class_names)

        return JSONResponse(content= {
            "success" : True,
            "filename": file.filename,
            "prediction": result
        })
    
    except Exception as e:
        raise HTTPException(status_code= 500, detail= f"Prediction error : {str(e)}")
    
@app.post("/predict_batch")
async def predict_batch(files: list[UploadFile] = File(...)):
    
    global model
    
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    results = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "File must be an image"
            })
            continue
        
        try:
            image_bytes = await file.read()
            prediction = predict(model, image_bytes, class_names)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "prediction": prediction
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    return JSONResponse(content={
        "success": True,
        "results": results,
        "total_files": len(files)
    })