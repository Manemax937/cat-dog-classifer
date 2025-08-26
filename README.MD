# 🖼️ Image Classification Web App

An end-to-end **image classification project** built with:

- ⚡ **FastAPI** – Python backend for ML inference  
- 🔥 **PyTorch** – Deep learning framework for training the model  
- 🌐 **Node.js + Express** – API Gateway & file handling  
- 🎨 **Frontend (HTML, CSS, JavaScript)** – User interface for uploading and viewing results  

---

## 🚀 Features
- Upload an image from the browser  
- Node.js server forwards the image to FastAPI  
- FastAPI loads a **PyTorch model** and predicts the class  
- Results are displayed back on the frontend  

---

## 🏗️ Project Architecture
Frontend (HTML/CSS/JS)
↓
Node.js API Gateway (Express + Multer)
↓
FastAPI (Python)
↓
PyTorch Model → Prediction