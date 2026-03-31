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
    
def is_heading(line:str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped)>60:
        return False
    lower = stripped.lower()
    starts_with_keyword = any(lower.startswith(kw) for kw in sectionNames)

    contains_keyword = stripped.isupper() and any(kw in lower for kw in sectionNames)
    return starts_with_keyword or contains_keyword

def clean_section_text(text:str)-> str:
    lines = text.splitlines()
    cleaned= []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r"^[\|\-\=\*\_\#]{2,}$", line):
            continue

        # Normalize bullet characters to a dash so TF-IDF
        # does not see "•", "▪", "✓" as distinct tokens
        line = re.sub(r"^[•▪◦▸✓\-–—]\s*", "- ", line)

        # Collapse internal whitespace
        line = re.sub(r"\s{2,}", " ", line)

        # Fix broken sentences: if a line ends mid-word (no punctuation,
        # next line starts lowercase) join them with a space.
        cleaned.append(line)
    
    joined = []
    i = 0
    while i < len(cleaned):
        current = cleaned[i]
        if (i + 1 < len(cleaned)
                and not current.endswith((".", ",", ":", ";", "-"))
                and cleaned[i + 1]
                and cleaned[i + 1][0].islower()):
            current = current + " " + cleaned[i + 1]
            i += 2
        else:
            joined.append(current)
            i += 1

    return "\n".join(joined).strip()
    


def split_text_into_chunks(text: str)-> str:
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = text.splitlines()

    sections: dict[str, str] = {}
    current_section = "Personal Details"
    current_lines: list[str] = []

    for line in lines:
        if not line.strip():
            continue

        if is_heading(line):
            # Flush accumulated lines into the current section
            if current_lines:
                results = "\n".join(current_lines)
                cleaned = clean_section_text(results)
                if cleaned:
                    sections[current_section] = cleaned
            current_section = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Flush the final section after the loop
    if current_lines:
        results = "\n".join(current_lines)
        cleaned = clean_section_text(results)
        if cleaned:
            sections[current_section] = cleaned

    sections = {k: v for k, v in sections.items() if v.strip()}

    if not sections or list(sections.keys()) == ["Personal Details"]:
        sections["Full Resume"] = clean_section_text(text)

    return sections

def parse_pdf(path) -> dict[str, str]:
    results = get_text_from_pdf(path)
    return split_text_into_chunks(results)

def parse_folder(path) -> dict[str, dict[str, str]]:
    folder = Path(path)
    
    if not folder.is_dir():
        raise ValueError(f"Expected a directory, got: {path!r}")
    return {f.name: parse_pdf(f) for f in folder.glob("*.pdf")}