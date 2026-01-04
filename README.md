# MCQ Generator App

An intelligent web application that transforms your documents into interactive multiple-choice quizzes using AI-powered question generation.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://mcq-generator-production-a0dc.up.railway.app/)

## Overview

MCQ Generator extracts meaningful content from PDF and DOCX documents and automatically generates high-quality multiple-choice questions. Built with Flask, PostgreSQL, and integrated LLM capabilities, it provides a complete quiz creation and management platform.

### Key Features

- 📄 Document upload and text extraction (PDF, DOCX)
- 🤖 AI-powered MCQ generation with configurable difficulty
- 👤 User authentication and session management
- 📊 Quiz tracking with detailed scoring and review
- 🎯 Question validation and quality control
- 🐳 Containerized deployment with Docker

## Tech Stack

- **Backend:** Flask with Blueprint architecture
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Frontend:** Jinja2 templates with Tailwind CSS
- **AI/ML:** LLM integration for question generation
- **Deployment:** Docker + Railway
- **Testing:** pytest

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- uv

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MedAliAdlouni/mcq-generator
   cd mcq-generator
   ```

2. **Set up virtual environment**
   ```bash
   uv venv
   source .venv/bin/activate 
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Configure environment variables**
   ```bash
   GEMINI_API_KEY=...
   FLASK_ENV=production
   SECRET_KEY=...
   DATABASE_URL=postgresql://mcq_user:POSTGRES_PASSWORD@localhost:5432/mcq_generator
   POSTGRES_USER=mcq_user
   POSTGRES_PASSWORD=meladlouni2001
   POSTGRES_DB=mcq_generator
   FLASK_PORT=5000
   POSTGRES_PORT=5432
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   uv run wsgi.py
   ```

Visit `http://localhost:5000` to access the application.

## How It Works

### 1. Document Processing

Users upload documents through the web interface. The extraction module (`core/extraction.py`) processes the file:
- Extracts text from PDF and DOCX formats
- Cleans and normalizes the content
- Splits text into semantic chunks optimized for question generation

### 2. Question Generation

The LLM module (`core/llm.py`) generates MCQs from extracted content:
- Formats prompts for the language model
- Generates questions with multiple distractors
- Validates and normalizes question quality
- Stores approved questions in the database

### 3. Quiz Management

The quiz lifecycle is managed through several components:
- **QuizSession:** Links questions to users and documents
- **Question Selection:** Intelligently selects questions based on difficulty
- **Answer Collection:** Tracks user responses in real-time
- **Scoring:** Calculates results and provides detailed feedback

### 4. Results & Analytics

Users can review their quiz performance:
- View correct and incorrect answers
- See explanations for each question
- Track progress over time
- Compare results across multiple attempts

### Customization

- **Question prompts:** Modify templates in `app/core/llm.py`
- **Chunking strategy:** Adjust parameters in `app/core/extraction.py`
- **Styling:** Edit Tailwind classes in templates or customize `static/css/`

## Troubleshooting

### Common Issues

**Low-quality questions generated:**
- Adjust prompt templates in `app/core/llm.py`
- Fine-tune chunking parameters in `app/core/extraction.py`
- Ensure input documents have clear, well-structured content

**Database connection errors:**
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`
- In Docker, use service names from `docker-compose.yml`
- Check PostgreSQL is running and accessible

**File upload failures:**
- Ensure `uploads/` directory exists and has write permissions
- Check file size limits in Flask config
- Verify supported file formats (PDF, DOCX)




**Live Demo:** [https://mcq-generator-production-a0dc.up.railway.app/](https://mcq-generator-production-a0dc.up.railway.app/)

**Issues?** Open an issue on GitHub or reach out via the repository.