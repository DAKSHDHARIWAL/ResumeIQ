

import re
import io
from collections import defaultdict

import pdfplumber
import docx
from sklearn.feature_extraction.text import TfidfVectorizer

from .skills_db import SKILLS_DB, SECTION_PATTERNS, ACTION_VERBS, WEAK_PHRASES

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/\S+", re.I)
GITHUB_RE = re.compile(r"github\.com/\S+", re.I)
NUMBER_RE = re.compile(r"(?<!\w)(\d+(\.\d+)?%|\$\d+|\d{2,}\+?)(?!\w)")
BULLET_LINE_RE = re.compile(r"^\s*[•\-\*\u2022\u25CF\u2023▪◦]\s*(.+)")

# Flatten the skills DB once into {lowercase_skill: (display_name, category)}
_ALL_SKILLS = []
for _category, _skills in SKILLS_DB.items():
    for _s in _skills:
        _ALL_SKILLS.append((_s, _category))
_SKILL_PATTERNS = [
    (name, category, re.compile(r"(?<![A-Za-z0-9+#./:])" + re.escape(name) + r"(?![A-Za-z0-9+#./:])", re.I))
    for name, category in _ALL_SKILLS
]


def extract_text(file_stream, filename):
    """Extract raw text from an uploaded resume file (pdf/docx/txt)."""
    name = filename.lower()
    data = file_stream.read()

    if name.endswith(".pdf"):
        text_parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        return "\n".join(text_parts)

    if name.endswith(".docx"):
        document = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs)

    # Fallback: treat as plain text
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def find_skills(text):
    """Return {category: [skills found]} using word-boundary matching."""
    found = defaultdict(list)
    for name, category, pattern in _SKILL_PATTERNS:
        if pattern.search(text):
            found[category].append(name)
    return dict(found)


def detect_sections(text):
    lower = text.lower()
    results = {}
    for section, patterns in SECTION_PATTERNS.items():
        results[section] = any(re.search(p, lower) for p in patterns)
    return results


def contact_info_check(text):
    return {
        "email": bool(EMAIL_RE.search(text)),
        "phone": bool(PHONE_RE.search(text)),
        "linkedin": bool(LINKEDIN_RE.search(text)),
        "github": bool(GITHUB_RE.search(text)),
    }


def writing_quality_check(text):
    lines = [l for l in text.split("\n") if l.strip()]
    bullet_lines = []
    for l in lines:
        m = BULLET_LINE_RE.match(l)
        if m:
            bullet_lines.append(m.group(1))
    # If no explicit bullet glyphs found, fall back to short lines as pseudo-bullets
    if not bullet_lines:
        bullet_lines = [l.strip() for l in lines if 3 <= len(l.split()) <= 25]

    total = max(len(bullet_lines), 1)
    action_verb_hits = 0
    quantified_hits = 0
    weak_hits = 0

    for b in bullet_lines:
        b_lower = b.strip().lower()
        first_word = b_lower.split()[0].strip(".,:;") if b_lower.split() else ""
        if first_word in ACTION_VERBS or any(b_lower.startswith(v) for v in ACTION_VERBS):
            action_verb_hits += 1
        if NUMBER_RE.search(b):
            quantified_hits += 1
        if any(w in b_lower for w in WEAK_PHRASES):
            weak_hits += 1

    return {
        "bullet_count": len(bullet_lines),
        "action_verb_ratio": round(action_verb_hits / total, 2),
        "quantified_ratio": round(quantified_hits / total, 2),
        "weak_phrase_count": weak_hits,
    }


def job_description_match(resume_text, jd_text):
    """TF-IDF similarity + skill-lexicon overlap between resume and JD."""
    # lowercase key -> canonical display name (e.g. "sql" -> "SQL"), so we
    # never mangle acronyms by title-casing them later.
    canonical = {name.lower(): name for name, _cat in _ALL_SKILLS}

    resume_skills = set()
    for cat, skills in find_skills(resume_text).items():
        resume_skills.update(s.lower() for s in skills)

    jd_skills = set()
    for cat, skills in find_skills(jd_text).items():
        jd_skills.update(s.lower() for s in skills)

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)

    skill_match_pct = round(100 * len(matched) / len(jd_skills), 1) if jd_skills else None

    # TF-IDF cosine similarity as a secondary, more holistic signal
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
        sim = (tfidf * tfidf.T).toarray()[0][1]
        similarity_pct = round(float(sim) * 100, 1)
    except Exception:
        similarity_pct = None

    return {
        "matched_skills": [canonical.get(s, s.title()) for s in matched],
        "missing_skills": [canonical.get(s, s.title()) for s in missing],
        "skill_match_percent": skill_match_pct,
        "text_similarity_percent": similarity_pct,
    }


def build_suggestions(sections, contact, writing, word_count, jd_result):
    suggestions = []

    for section, present in sections.items():
        if not present and section != "Contact Information":
            suggestions.append(f"Add a clearly labeled \u201c{section}\u201d section — it looks missing.")

    if not contact.get("email"):
        suggestions.append("Include a professional email address near the top of your resume.")
    if not contact.get("phone"):
        suggestions.append("Add a phone number so recruiters can reach you directly.")
    if not contact.get("linkedin"):
        suggestions.append("Add your LinkedIn profile URL to boost credibility.")

    if writing["action_verb_ratio"] < 0.4:
        suggestions.append("Start more bullet points with strong action verbs (Built, Led, Improved) instead of passive phrasing.")
    if writing["weak_phrase_count"] > 0:
        suggestions.append("Replace weak phrases like \u201cresponsible for\u201d or \u201cworked on\u201d with direct accomplishment statements.")
    if writing["quantified_ratio"] < 0.3:
        suggestions.append("Quantify more achievements with numbers, percentages, or metrics (e.g. \u201creduced load time by 30%\u201d).")

    if word_count < 250:
        suggestions.append("Your resume looks short — consider adding more detail on projects and experience.")
    elif word_count > 900:
        suggestions.append("Your resume is quite long — trim it toward 1 focused page (roughly 400–700 words) if you're early-career.")

    if jd_result and jd_result.get("missing_skills"):
        top_missing = jd_result["missing_skills"][:6]
        if top_missing:
            suggestions.append(
                "The job description mentions skills not found in your resume: " + ", ".join(top_missing) + "."
            )

    if not suggestions:
        suggestions.append("Solid resume! Only minor polish left — proofread carefully and tailor keywords per job.")

    return suggestions


def score_resume(sections, contact, writing, word_count, jd_result):
    """Composite score out of 100. Each component is transparent and explainable."""
    section_score = 100 * sum(sections.values()) / len(sections)

    contact_score = 100 * sum(contact.values()) / len(contact)

    writing_score = 100 * (
        0.5 * min(writing["action_verb_ratio"], 1)
        + 0.5 * min(writing["quantified_ratio"], 1)
    )
    writing_score = max(0, writing_score - writing["weak_phrase_count"] * 5)

    if 350 <= word_count <= 850:
        length_score = 100
    elif word_count < 350:
        length_score = max(0, 100 - (350 - word_count) / 3)
    else:
        length_score = max(0, 100 - (word_count - 850) / 6)

    base_quality = (
        0.30 * section_score
        + 0.15 * contact_score
        + 0.35 * writing_score
        + 0.20 * length_score
    )

    breakdown = {
        "Section Completeness": round(section_score),
        "Contact Info": round(contact_score),
        "Writing Quality": round(writing_score),
        "Length / Format": round(length_score),
    }

    if jd_result and jd_result.get("skill_match_percent") is not None:
        jd_score = jd_result["skill_match_percent"]
        breakdown["Job Description Match"] = round(jd_score)
        overall = round(0.55 * jd_score + 0.45 * base_quality)
    else:
        overall = round(base_quality)

    return overall, breakdown


def analyze_resume(resume_text, jd_text=None):
    sections = detect_sections(resume_text)
    contact = contact_info_check(resume_text)
    writing = writing_quality_check(resume_text)
    word_count = len(resume_text.split())
    skills_found = find_skills(resume_text)

    jd_result = job_description_match(resume_text, jd_text) if jd_text and jd_text.strip() else None

    overall, breakdown = score_resume(sections, contact, writing, word_count, jd_result)
    suggestions = build_suggestions(sections, contact, writing, word_count, jd_result)

    return {
        "overall_score": overall,
        "score_breakdown": breakdown,
        "sections": sections,
        "contact_info": contact,
        "writing_quality": writing,
        "word_count": word_count,
        "skills_found": skills_found,
        "skills_found_count": sum(len(v) for v in skills_found.values()),
        "job_match": jd_result,
        "suggestions": suggestions,
    }