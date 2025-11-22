DocuMagic – Intelligent Document Processing Platform

DocuMagic is an end-to-end automated document ingestion, parsing, classification, and storage solution built with FastAPI, PostgreSQL, and modern NLP/AI capabilities.
It accelerates enterprise workflows by turning raw documents into structured, searchable insights.

🚀 Key Features

Email Ingestion Pipeline
Automatically fetch emails + attachments from configured mailboxes.

Document Parsing Engine
Extract text, tables, metadata, and entities using Python libraries & custom logic.

Metadata Extraction & Classification
Categorize documents using rules or ML-driven classification.

Secure Storage Layer
Save parsed documents and metadata in PostgreSQL + file/object storage.

REST API with FastAPI
Clean, fast, async API for consumption by dashboards or other systems.

Streamlit Dashboard (Optional)
Business-friendly interface to view processed documents.

Automation & Scheduling
Background jobs for periodic ingestion, cleaning, and reporting.

🏗️ Tech Stack
Layer	Technology
Backend API	FastAPI
Database	PostgreSQL
ORM	SQLAlchemy
Document Processing	PyPDF2, pdfminer, Tesseract, custom NLP
Email Client	IMAP / SMTP
Dashboard	Streamlit
Deployment	Docker, Uvicorn, Gunicorn
Cloud	Azure / AWS (optional integrations)
📦 Project Structure
DocuMagic/
│── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   ├── utils/
│   └── main.py
│
│── tests/
│── requirements.txt
│── README.md
│── docker-compose.yml
│── .env.example
