def format_top_resumes_for_llm(
    ranked_resumes: list[dict],          # output from retrieve_top_resumes()
    jd_text: str,
    max_chars_per_resume: int = 3500,
    include_score: bool = True,
    include_filename: bool = True
) -> str:
    """
    Creates a clean prompt-ready string containing:
    - The job description
    - Top N resumes with their overall score and concatenated relevant text
    Input example:
    ranked_resumes = [
        {"filename": "...", "overall_score": 89.4, "chunks": [...]},
        ...
    ]
    """
    if not ranked_resumes:
        return "No suitable resumes found."
 
    parts = [f"Job Description:\n{jd_text.strip()}\n", "=" * 60]
 
    for resume in ranked_resumes:
        filename = resume.get("filename", "Unnamed resume")
        score = resume.get("overall_score", "?")
        chunks = resume.get("chunks", [])
 
        if not chunks:
            continue
 
        # Collect text from all chunks of this resume
        resume_text_parts = []
        for chunk in chunks:
            section = chunk.get("section", "Section")
            text = chunk.get("text", "").strip()
            if text:
                resume_text_parts.append(f"[{section}]\n{text}")
 
        resume_content = "\n\n".join(resume_text_parts)
 
        # Truncate if too long
        if len(resume_content) > max_chars_per_resume:
            resume_content = resume_content[:max_chars_per_resume] + " ... [truncated]"
 
        # Build resume block
        header = f"Resume: {filename}"
        if include_score:
            header += f"  —  Overall match score: {score}/100"
 
        parts.append(header)
        parts.append("-" * len(header))
        parts.append(resume_content)
        parts.append("")  # spacing between resumes
 
    full_context = "\n".join(parts).strip()
 
    return full_context