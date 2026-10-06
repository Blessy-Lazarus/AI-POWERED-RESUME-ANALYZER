import os
import subprocess
import pytesseract
import docx
import pdfplumber
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import re
import pandas as pd
import openai

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'E:\path\to\tesseract-main\tesseract.exe'

# Function to check if Tesseract is installed
def check_tesseract_installed():
    try:
        result = subprocess.run(['tesseract', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("Tesseract is installed and accessible.")
        else:
            print("Tesseract is not installed or not in your PATH.")
    except FileNotFoundError:
        print("Tesseract is not installed or not in your PATH.")

# Check if Tesseract is installed
check_tesseract_installed()

# Download necessary NLTK resources
nltk.download('punkt', force=True)
nltk.download('averaged_perceptron_tagger', force=True)
nltk.download('maxent_ne_chunker', force=True)
nltk.download('words', force=True)

# Load dataset directly from Kaggle
path = "path_to_dataset"
dataset = pd.read_csv(os.path.join(path, "resume_dataset.csv"))
X_train, X_test, y_train, y_test = train_test_split(dataset['Resume'], dataset['Category'], test_size=0.2, random_state=42)

# Train a more advanced ML model (Random Forest)
model = make_pipeline(TfidfVectorizer(stop_words='english'), RandomForestClassifier(n_estimators=100, random_state=42))
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(f"Model Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")

# Set up OpenAI API key
openai.api_key = 'your-openai-api-key'

def analyze_resume_with_llm(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Analyze the following resume text and extract the following information:\n\n1. Skills\n2. Job Recommendations\n3. Learning Roadmap\n\nResume Text:\n{text}"}
            ],
            max_tokens=500
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        # Return a default message when the quota is exceeded
        return "LLM analysis is currently unavailable due to API quota limits. Please try again later."

def roadmap_suggestions(skills):
    roadmap = {
        "python": "https://www.python.org/doc/",
        "machine learning": "https://www.coursera.org/learn/machine-learning",
        "cloud computing": "https://aws.amazon.com/training/",
        "sql": "https://www.w3schools.com/sql/",
        "nlp": "https://www.coursera.org/learn/natural-language-processing",
        "data science": "https://www.coursera.org/specializations/jhu-data-science",
        "java": "https://www.codecademy.com/learn/learn-java"
    }
    return {skill: roadmap.get(skill, "No roadmap available") for skill in skills}

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^a-z\s]', '', text)
    # Tokenize text
    words = word_tokenize(text)
    return ' '.join(words)

def analyze_resume(text):
    text = preprocess_text(text)
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    word_count = len(words)
    sentence_count = len(sentences)
    keyword_counts = Counter(re.findall(r'\b(skills?|experience|education|projects?|certifications?|leadership)\b', text, re.IGNORECASE))

    structured = word_count > 100 and len(keyword_counts) > 3  # Simple heuristic for structure
    score = min(100, len(keyword_counts) * 10 + word_count // 10)

    prediction = model.predict([text])[0]  # Predict category
    extracted_skills = extract_skills(text)
    job_recommendations = recommend_jobs(extracted_skills)

    llm_analysis = analyze_resume_with_llm(text)

    return score, structured, extracted_skills, job_recommendations, llm_analysis

def extract_resume_text(file_path):
    if file_path.endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages])
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    elif file_path.endswith('.png') or file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
        except pytesseract.pytesseract.TesseractNotFoundError:
            return "Error: Tesseract is not installed or it's not in your PATH. Please install Tesseract OCR."
    else:
        raise ValueError("Unsupported file format")
    return text

def extract_skills(text):
    skills = {"python", "java", "machine learning", "deep learning", "nlp", "data science", "cloud computing", "sql", "tableau"}
    extracted_skills = [skill for skill in skills if skill in text.lower()]
    return extracted_skills

def recommend_jobs(skills):
    return ["Data Scientist", "Machine Learning Engineer", "Software Developer"]

def extract_skills_from_description(description):
    skills = {"python", "java", "machine learning", "deep learning", "nlp", "data science", "cloud computing", "sql", "tableau"}
    extracted_skills = [skill for skill in skills if skill in description.lower()]
    return extracted_skills

def generate_html_report(score, structured, extracted_skills, job_recommendations, llm_analysis, job_openings_by_description=None, roadmap_by_description=None):
    html_content = f"""
    <html>
    <head>
        <title>Resume Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .section {{ margin-bottom: 20px; }}
            .job-links a {{ display: block; margin: 5px 0; color: blue; text-decoration: none; }}
            .job-links a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>Resume Analysis Report</h1>
        <div class="section">
            <h2>Resume Score</h2>
            <p>Score: {score}/100</p>
            <p>Structured: {'Yes' if structured else 'No'}</p>
        </div>
        <div class="section">
            <h2>Extracted Skills</h2>
            <p>{', '.join(extracted_skills) if extracted_skills else 'No skills identified'}</p>
        </div>
        <div class="section">
            <h2>Job Recommendations</h2>
            <p>{', '.join(job_recommendations)}</p>
        </div>
    """
    if job_openings_by_description:
        html_content += """
            <div class="section">
                <h2>Job Openings Based on Description</h2>
                <div class="job-links">
        """
        for platform, link in job_openings_by_description.items():
            html_content += f'<li><a href="{link}" target="_blank">{platform} - Apply Now</a></li>'
        html_content += "</ul></div></div>"

    if roadmap_by_description:
        html_content += """
            <div class="section">
                <h2>Learning Roadmap Based on Job Description</h2>
        """
        for skill, link in roadmap_by_description.items():
            html_content += f'<p><strong>{skill.capitalize()}:</strong> <a href="{link}" target="_blank">{link}</a></p>'
        html_content += "</div>"

    html_content += f"""
        <div class="section">
            <h2>LLM Analysis</h2>
            <p>{llm_analysis}</p>
        </div>
    </body>
    </html>
    """
    return html_content