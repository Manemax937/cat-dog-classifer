const express = require("express");
const multer = require("multer");
const fetch = require("node-fetch");
const FormData = require("form-data");
const fs = require("fs");
const path = require("path");

const app = express();
const upload = multer({ dest: "uploads/" });

app.use(express.static(path.join(__dirname, "public")));

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

app.get("/", (req, res) => {
  res.json({ 
    message: "Node.js API Gateway is running!",
    endpoints: {
      upload: "POST /upload",
      health: "GET /health"
    }
  });
});

app.get("/health", async (req, res) => {
  try {
    const response = await fetch("http://127.0.0.1:8000/health");
    const result = await response.json();
    res.json({
      gateway: "healthy",
      python_api: result
    });
  } catch (error) {
    res.status(500).json({
      gateway: "healthy", 
      python_api: "unhealthy",
      error: error.message
    });
  }
});

app.post("/upload", upload.single("file"), async (req, res) => {
  console.log("📁 Upload request received");
  
  try {
    if (!req.file) {
      return res.status(400).json({ 
        success: false, 
        error: "No file uploaded" 
      });
    }

    console.log("📄 File details:", {
      filename: req.file.filename,
      originalname: req.file.originalname,
      size: req.file.size,
      path: req.file.path
    });

    const form = new FormData();
    form.append("file", fs.createReadStream(req.file.path), {
      filename: req.file.originalname,
      contentType: req.file.mimetype || 'image/jpeg'
    });

    console.log("🚀 Sending request to Python API...");

    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      body: form,
      headers: form.getHeaders()
    });

    console.log("📡 Python API response status:", response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("❌ Python API error:", errorText);
      return res.status(response.status).json({
        success: false,
        error: `Python API error: ${errorText}`
      });
    }

    const result = await response.json();
    console.log("✅ Prediction result:", result);

    fs.unlink(req.file.path, (err) => {
      if (err) console.error("Error deleting temp file:", err);
    });

    res.json({
      success: true,
      ...result
    });

  } catch (error) {
    console.error("❌ Server error:", error);
    
    if (req.file && req.file.path) {
      fs.unlink(req.file.path, (err) => {
        if (err) console.error("Error deleting temp file:", err);
      });
    }

    res.status(500).json({ 
      success: false,
      error: error.message 
    });
  }
});

app.use((error, req, res, next) => {
  console.error("💥 Unhandled error:", error);
  res.status(500).json({
    success: false,
    error: "Internal server error"
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Node.js server running on http://localhost:${PORT}`);
  console.log(`📚 Test endpoints:`);
  console.log(`   Health: http://localhost:${PORT}/health`);
  console.log(`   Upload: POST http://localhost:${PORT}/upload`);
});

process.on('SIGINT', () => {
  console.log('\n👋 Shutting down gracefully...');
  process.exit(0);
});
