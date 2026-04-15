from docx import Document

def normalize_alignment(alignment):
    try:
        if hasattr(alignment, "name"):
            return alignment.name.lower()
        return str(alignment).lower()
    except Exception:
        return "left"

def parse_docx(path: str):
    doc = Document(path)

    data = {
        "paragraphs": [],
        "sections": doc.sections,
        "full_text": ""
    }

    for i, p in enumerate(doc.paragraphs):
        runs = []

        for r in p.runs:
            runs.append({
                "text": r.text,
                "font": r.font.name,
                "size": r.font.size.pt if r.font.size else None,
                "bold": r.bold,
                "italic": r.italic
            })

        try:
            alignment = normalize_alignment(p.alignment)
        except Exception:
            alignment = "left"

        data["paragraphs"].append({
            "index": i,
            "text": p.text,
            "alignment": alignment,
            "indent": p.paragraph_format.first_line_indent,
            "spacing": p.paragraph_format.line_spacing,
            "runs": runs
        })

        data["full_text"] += p.text + "\n"

    return data