# AI-Powered Resume Analyzer & Job Recommendation System 

An intelligent, full-stack recruitment automation engine designed to parse unstructured resume data, categorize professional domains, conduct deep semantic gap analysis, and map personalized learning paths for job seekers.

---

## Tech Stack & Key Frameworks
- **Core Language:** Python 3.9+
- **Machine Learning & NLP:** Scikit-Learn (SVM, Logistic Regression), NLTK (Tokenization, POS Tagging)
- **Generative AI & NLU:** OpenAI GPT API (Semantic Analysis & Contextual Matching)
- **Document Ingestion (OCR):** `pdfplumber`, `python-docx`, `pytesseract`
- **Frontend / Interface:** Flask (Localhost Server Dashboard)
- **Data Engineering:** Pandas, TF-IDF Vectorization





## System Architecture & Workflow
The system establishes an end-to-end automated processing pipeline spanning five core modular phases:
```text
[ Data Analysis ] ──> [ Recommendation Engine ] ──> [ Quality Analysis ] ──> [ Market Integration ] ──> [ Resource Curation ]
  - PDF/Image OCR       - Content Filtering          - Section Evaluation     - LinkedIn Links           - Custom Roadmaps
  - TF-IDF Vectors      - Cosine Similarity          - Keyword Scoring        - Glassdoor Links          - Certification Links
```
1. **Multi-Format Ingestion:** Extracts raw strings from PDF, Word documents, and image-based attachments via specialized text parsers and regular expression cleanup.
2. **Hybrid Machine Learning Classification:** Maps the unstructured text data to labeled Kaggle resume vectors using an 80/20 train-test split over robust SVM architectures.
3. **LLM Contextual Matching:** Transcends primitive keyword matching by routing extracted skills through OpenAI's GPT models to execute dynamic, semantic alignment against targeted job requirements.
4. **Automated Skill-Gap Reporting:** Analyzes missing competencies and automatically pulls structural developer roadmaps directly from open-access resource engines like `roadmap.sh`.
5. **Direct Recruitment Channels:** Automatically constructs targeted job search endpoint links targeting explicit geolocation vectors across LinkedIn and Glassdoor dashboards.

---

##  Application Dashboard Preview
### 1. Central Portal & Authentication
The landing dashboard prompts candidates to submit secure profile verification before interacting with the core parsing neural layers.

### 2. File Processing Portal & Analysis Readout
Enables instant upload for active candidate profiles along with a direct textbox to accept target company job descriptions for deep cross-referencing.

The analysis layout calculates a quantitative resume quality score (e.g., 94/100) alongside domain field predictions and live external career redirect links.

---
## Installation & Local Environment Setup
### 1. Clone the Repository
```bash
git clone https://github.com
cd AI-Resume-Analyzer
```
### 2. Configure Environment Variables
Create a secure `.env` file in the root directory and append your private OpenAI key:
```env
OPENAI_API_KEY=your_secret_api_key_here
FLASK_APP=app.py
```
### 3. Install Target Production Requirements
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Deploy the Localhost Dashboard Server
```bash
flask run --port=5000
```
