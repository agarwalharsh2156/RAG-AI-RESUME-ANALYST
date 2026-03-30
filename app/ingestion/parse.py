import fitz
import re
from pathlib import Path

sectionNames =  [
        "personal", "contact", "profile", "summary", "about",
        "education", "qualification", "academic",
        "experience", "work", "employment", "professional",
        "skills", "technical", "competencies",
        "project", "projects",
        "certifications", "certification", "certificate", "award", "achievement", "achievements",
        "language", "languages",
        "interest", "interests", "hobbies"
    ]

def get_text_from_pdf(pdf_path):
    with fitz.open(str(pdf_path)) as doc:
        return "\n".join(page.get_text("text") for page in doc).strip()

def split_text_into_chunks(text):
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"\.\s*", ". ", text)
    text = re.sub(r"([a-zA-Z])\s*\n([a-zA-Z])", r"\1 \2", text)

    lines = text.splitlines()

    sections = {}
    currentSection = "Personal Details"
    currentLine = []

    for line in lines:  
        if not line.strip():
            continue
        clean_line = line.strip()
        lower = clean_line.lower()
        is_section = ( any(lower.startswith(s) for s in sectionNames) and len(clean_line) <= 50)

        if is_section:

            if currentLine:
                content = "\n".join(currentLine).strip()
                if content:
                    sections[currentSection] = content
            
            currentSection = clean_line
            currentLine = []

        else:
            currentLine.append(clean_line)

    if currentLine:
        content = "\n".join(currentLine).strip()
        if content:
            sections[currentSection] = content

    sections = {k: v for k, v in sections.items() if v}
    
    if len(sections) == 0 or ("Personal Details" in sections and len(sections) == 1):
        sections["Full Resume"] = text
        
    return sections

def parse_pdf(path):
    results = get_text_from_pdf(path)
    sections = split_text_into_chunks(results)
    return sections

def parse_folder(path):
    folder = Path(path)
    
    if not folder.is_dir():
        raise ValueError("Invalid folder")
    parsed_resumes = {}

    for file in folder.glob("*.pdf"):
        parsed_resumes[file.name] = parse_pdf(file)
    
    return parsed_resumes

