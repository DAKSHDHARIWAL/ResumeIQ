# ResumeIQ — AI Resume Analyzer

<p align="center">
  <strong>Turn a resume into actionable career feedback.</strong><br>
  Upload a PDF, DOCX, or TXT resume to review its structure, writing signals, skills, and alignment with a target job description.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/Flask-3.1-black?logo=flask">
  <img alt="NLP" src="https://img.shields.io/badge/NLP-TF--IDF-7C3AED">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-22C55E.svg">
</p>

---

## ✨ Overview

**ResumeIQ** is a Flask-based resume analysis web app that combines document text extraction, rule-based resume checks, skill detection, and classic NLP to produce understandable feedback. Add a job description to evaluate lexical alignment between the resume and the role.

> **Important:** ResumeIQ uses a transparent, rule-based scoring pipeline and TF-IDF text similarity. It is not a trained deep-learning model, and its score should be treated as guidance—not a hiring decision or a guarantee of job fit.

## 🚀 Features

- **Multiple file formats:** PDF, DOCX, and TXT.
- **Resume quality signals:** checks for common sections, contact details, writing patterns, and approximate length.
- **Skill detection:** matches resume text against a curated skills lexicon.
- **Job-description comparison:** uses TF-IDF similarity and keyword matching when a job description is supplied.
- **Actionable suggestions:** highlights areas that may deserve attention.
- **Interactive interface:** responsive HTML/CSS/JavaScript frontend with an animated Three.js hero visual.
- **Lightweight API:** Flask endpoint for analysis and a health-check endpoint.

## 🧰 Tech stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask |
| Document extraction | `pdfplumber`, `python-docx` |
| Text analysis | Rule-based patterns, curated skills lexicon, scikit-learn TF-IDF |
| Frontend | HTML, CSS, vanilla JavaScript |
| Visual effects | Three.js |

## 📁 Project structure

```text
ResumeIQ/
├── app.py                    # Flask app and API routes
├── requirements.txt          # Python dependencies
├── resume_parser/
│   ├── __init__.py
│   ├── analyzer.py           # Extraction, scoring, and suggestions
│   └── skills_db.py          # Skills lexicon and text patterns
├── templates/
│   └── index.html            # Main web interface
├── static/
│   ├── css/style.css         # Styling and responsive layout
│   └── js/
│       ├── main.js           # Upload and results interactions
│       └── three-bg.js       # Three.js background visual
├── .gitignore
└── LICENSE
```

## ⚙️ Run locally

### 1. Requirements

- Python 3.10 or newer recommended
- `pip`
- A modern web browser

### 2. Clone the repository

```bash
git clone https://github.com/DAKSHDHARIWAL/ResumeIQ.git
cd ResumeIQ
```

### 3. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies and start the app

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## 🔍 API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serves the web interface |
| `POST` | `/api/analyze` | Analyzes an uploaded resume; accepts `resume` and optional `job_description` as multipart form fields |
| `GET` | `/api/health` | Returns a basic health status |

The upload limit is currently **5 MB**. Supported extensions are PDF, DOCX, and TXT.

## 🧠 How the score is estimated

The current implementation uses a transparent heuristic pipeline. Without a job description, the base score considers these dimensions:

| Dimension | Weight |
|---|---:|
| Section completeness | 30% |
| Contact information | 15% |
| Writing quality signals | 35% |
| Length and formatting signals | 20% |

When a job description is provided, the implementation blends job-description keyword alignment with the base resume-quality score. The exact calculations live in `resume_parser/analyzer.py`; consult that file when modifying or presenting the scoring method.

## 🔐 Privacy and responsible use

- Analyze resumes you have permission to process.
- Resume text can contain personal information; avoid uploading real resumes to public issue trackers or sharing analysis output publicly.
- This project is a learning and feedback tool. Review suggestions manually and do not use its score as the sole basis for hiring or career decisions.
- The app processes uploaded content in the request and does not currently provide a persistent analysis-history feature.

## 🛠️ Ideas for future improvements

- Add automated tests for document extraction and scoring edge cases.
- Improve support for scanned PDFs through optional OCR.
- Add configurable skill dictionaries and explainable score details.
- Add accessibility checks and a dedicated results export.
- Evaluate semantic similarity methods against a labelled test set before replacing TF-IDF.

## 🤝 Contributing

Issues and pull requests are welcome. For substantial changes, please open an issue first to discuss the proposed approach. Keep contributions focused, documented, and privacy-conscious.

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

<p align="center">Built as a practical project to explore Python, Flask, document parsing, and explainable text analysis.</p>