import fitz
import re
from pathlib import Path

def get_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    doc.close()
    return text.strip()

def split_text_into_chunks(text):
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"\.\s*", ". ", text)
    text = re.sub(r"(a-zA-Z)\n(a-zA-z)", "\1 \2", text)

    lines = text.splitlines()
    sections = {}
    currentSection = "Personal Details"
    currentLine = []

    sectionNames =  [
        "personal", "contact", "profile", "summary", "about",
        "education", "qualification", "academic",
        "experience", "work", "employment", "professional",
        "skills", "technical", "competencies",
        "project", "projects",
        "certification", "certificate", "award", "achievement",
        "language", "languages",
        "interest", "hobbies"
    ]

    for line in lines:
        clean_line = line.strip().lower()
        if not line:
            continue
        is_section = any(clean_line.startswith(s) for s in sectionNames)
        if is_section:
            content = "\n".join(currentLine).strip()
            if content:
                sections[currentSection] = content
            currentSection = clean_line
            content = []
        else:
            currentLine.append(clean_line)

        if currentLine:
            content = "\n".join(currentLine).strip()
            if content:
                sections[currentSection] = content
    
    if len(sections) == 0 or "Personal Details" in sections:
        sections["Full Resume"] = text
        
    return sections

def parse_pdf(path):
    results = get_text_from_pdf(path)
    sections = split_text_into_chunks(results)
    return sections

def parse_folder(path):
    folder = Path(path)
    parsed_resumes = {}
    if folder.is_dir():
        for file in folder.glob("*.pdf"):
            parsed_resumes[file.name] = parse_pdf(file)
        return parsed_resumes
    else:
        print("Invalid folder")
        return {}


        


