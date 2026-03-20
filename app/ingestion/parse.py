import hashlib;
import re;
from dataclasses import dataclass, field;
from pathlib import Path;

import fitz


#Extraction
@dataclass
class ResumeChunk:
    doc_id: str
    chunk_id: str
    text: str
    section: str
    metadata: dict = field(default_factory= dict)

    def to_dict(self):
        return {
            "doc_id": self.doc_id,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "section": self.section,
            "metadata": self.metadata,
        }
    

#Cleaning
@dataclass
class ResumeDocument:
    file_name: str
    doc_id:    str
    raw_text:  str
    sections:  dict[str, str]
    chunks:    list[ResumeChunk]

    def to_dict(self):
        return {
            "doc_id":    self.doc_id,
            "file_name": self.file_name,
            "sections":  self.sections,
            "chunks":    [c.to_dict() for c in self.chunks],
        }


#
def _extract(path: Path) -> str:
    doc   = fitz.open(str(path))
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n\n".join(pages)



def _clean(text: str) -> str:
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()



_SECTION_RE = re.compile(
    r"^"
    r"[•\-\*]?\s*"
    r"(?P<heading>"
    r"contact(?: info(?:rmation)?)?"
    r"|summary|objective|profile|about(?: me)?"
    r"|professional\s*summary|career\s*summary"
    r"|(?:work\s)?experience(?:\s*[-–—:].*)?"
    r"|project\s*experience(?:\s*[-–—:].*)?"
    r"|employment(?: history)?"
    r"|internship"
    r"|education(?: & training)?"
    r"|(?:technical|core|key|professional)?\s*skills?"
    r"(?:\s*&\s*(?:expertise|competencies|abilities))?"
    r"|certifications?|licenses?|courses?"
    r"|projects?(?:\s*[-–—:].*)?"
    r"|personal\s*projects?(?:\s*[-–—:].*)?"
    r"|academic\s*projects?(?:\s*[-–—:].*)?"
    r"|awards?|achievements?|honors?|accomplishments?"
    r"|publications?|research"
    r"|languages?"
    r"|interests?|hobbies"
    r"|references?"
    r"|volunteering|extra.curricular"
    r")"
    r":?\s*$",
    re.IGNORECASE | re.MULTILINE,
)



def _split_sections(text: str) -> dict[str, str]:

    matches = list(_SECTION_RE.finditer(text))

    if not matches:
        return {"full_text": text.strip()}

    sections: dict[str, str] = {}

    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections["contact"] = preamble

    for i, m in enumerate(matches):
        heading = m.group("heading").strip().lower()
        start   = m.end()
        end     = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body    = text[start:end].strip()
        if body:
            sections[heading] = body

    return sections



def _chunk(
    text:      str,
    section:   str,
    doc_id:    str,
    file_name: str,
    size:      int = 400,
    overlap:   int = 80,
) -> list[ResumeChunk]:
    
    words  = text.split()
    chunks = []
    start  = 0

    while start < len(words):
        end  = min(start + size, len(words))
        chunks.append(ResumeChunk(
            doc_id   = doc_id,
            chunk_id = f"{doc_id[:8]}_{section.replace(' ', '_')}_{len(chunks)}",
            text     = " ".join(words[start:end]),
            section  = section,
            metadata = {
                "file_name":   file_name,
                "section":     section,
                "chunk_index": len(chunks),
                "word_count":  end - start,
            },
        ))
        if end == len(words):
            break
        start += size - overlap

    return chunks



def parse_resume(
    file_path:  str,
    chunk_size: int = 400,
    overlap:    int = 80,
) -> ResumeDocument:
    
    path= Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() !=".pdf":
        raise ValueError(f"Expected .pdf, got: {path.suffix}")
    
    raw = _clean(_extract(path))

    if not raw:
        raise ValueError(f"Text mot found '{path.name}' may be image-based.")
    
    doc_id = hashlib.sha256(raw.encode()).hexdigest()

    sections= _split_sections(raw)

    chunks: list[ResumeChunk] = []

    for section, body in sections.items():
        body= _clean(body)
        if body:
            chunks.extend(
                _chunk(body, section, doc_id, path.name, chunk_size, overlap)
            )
    
    return ResumeDocument(
        file_name=path.name,
        doc_id= doc_id,
        raw_text= raw,
        sections= sections,
        chunks= chunks
    )

if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python parse.py resume.pdf")
        print("  python parse.py audit ./resumes")
        sys.exit(1)

    doc = parse_resume(sys.argv[1])
    out = doc.to_dict()
    out.pop("raw_text", None)

    print(json.dumps(out, indent=2))
    print(f"\n✓ {len(doc.chunks)} chunks | sections: {list(doc.sections.keys())}")
    print(f"  doc_id: {doc.doc_id[:16]}...")