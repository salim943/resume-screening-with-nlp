from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import docx2txt
from pdfminer.high_level import extract_text
import spacy
import mysql.connector
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'resumes/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize spaCy
nlp = spacy.load("en_core_web_sm")

# Database connection
db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)
cursor = db.cursor()

# Extract text from resume file
def extract_resume_text(filepath):
    if filepath.lower().endswith(".pdf"):
        return extract_text(filepath)
    elif filepath.lower().endswith(".docx"):
        return docx2txt.process(filepath)
    else:
        return ""

# Parse basic info from resume text
def parse_resume_text(text):
    doc = nlp(text)
    name = ""
    email = ""
    phone = ""
    skills = []

    # Extract PERSON entities as name
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
        elif ent.label_ == "ORG":
            skills.append(ent.text)  # crude way for skills/org names

    # Extract email and phone using regex
    email_match = re.search(r"\b[\w.-]+@[\w.-]+\.\w{2,4}\b", text)
    phone_match = re.search(r"\b\d{10,15}\b", text)

    email = email_match.group() if email_match else ""
    phone = phone_match.group() if phone_match else ""

    return {
        "name": name,
        "email": email,
        "mobile_number": phone,
        "skills": skills,
        "education": "",   # optional
        "total_experience": 0  # optional
    }

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Extract text
    text = extract_resume_text(filepath)
    if not text:
        return jsonify({'error': 'Unable to read resume'}), 400

    # Parse info from text
    data = parse_resume_text(text)

    # Save to MySQL
    cursor.execute("""
        INSERT INTO candidates (name, email, phone, skills, experience, education, resume_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data["name"], data["email"], data["mobile_number"],
        ', '.join(data["skills"]), data["total_experience"],
        data["education"], filepath
    ))
    db.commit()

    return jsonify({'message': 'Resume uploaded successfully', 'data': data})

if __name__ == '__main__':
    app.run(debug=True)
