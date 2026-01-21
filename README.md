# Motor Insurance PDF OCR & Data Extraction

A production-ready Flask-based OCR service that extracts structured data from Motor Insurance Policy PDFs and returns clean, schema-compliant output.  
The system supports both text-based PDFs and scanned/image PDFs using OCR.

---

## 🚀 Features

- Supports multiple insurance PDF layouts
- Automatic detection of text-based vs scanned PDFs
- OCR fallback using Tesseract
- Strict and consistent output schema
- Safe handling of missing or ambiguous fields
- Deployed on Vercel (serverless Flask)

---

## 🧩 Tech Stack

Backend: Flask (Python)  
OCR Engine: Tesseract OCR  
PDF Processing: PyMuPDF  
Image Processing: Pillow  
Deployment: Vercel (Serverless)

---

## 📂 Project Structure

.
├── api/
│   └── index.py          # Vercel entrypoint
├── ocr_pdf_ext.py        # OCR + PDF text extraction logic
├── requirements.txt     # Python dependencies
├── vercel.json           # Vercel routing config
├── README.md
└── .gitignore

---

## ⚙️ Local Setup

Create virtual environment:

python -m venv venv  
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Install Tesseract OCR:

macOS:
brew install tesseract

Ubuntu:
sudo apt install tesseract-ocr

---

## ▶️ Run Locally

python ocr_pdf_ext.py path/to/sample.pdf

Optional output to file:

python ocr_pdf_ext.py sample.pdf --output output.txt

---

## ☁️ Live Deployment

Production URL:
https://motor-insurance-ocr.vercel.app

The service is deployed as a serverless Flask app using Vercel.

---

## 🧪 Use Cases

Insurance document digitization  
Policy data normalization  
Backend preprocessing for ML and analytics  
Automated document pipelines

---

## 🛠️ Future Enhancements

JSON schema validation  
Confidence scoring for extracted fields  
Support for additional insurance document types  
Batch PDF processing  
REST API endpoints for uploads

---

## 👤 Author

Developed by Vishal Godara  
GitHub: https://github.com/vishal-24o

---

## 📄 License

This project is open-source and available under the MIT License.
