"""
DOCX Document Processor & Media Archive Packager
===============================================
Handles text PII redaction across all paragraphs, tables, headers, and footers in a .docx file,
and patches embedded media image binaries directly inside the docx ZIP archive structure.
"""

import os
import io
import zipfile
import shutil
import docx
from docx import Document
from PIL import Image
from .engine import PIIRedactor
from .image_redactor import redact_pan_card_pil, redact_aadhaar_card_pil

def redact_paragraph(p, redactor: PIIRedactor) -> int:
    """Redacts PII in a paragraph while preserving paragraph and run formatting."""
    if not p.text or not p.text.strip():
        return 0

    orig_text = p.text
    redacted_text, entities = redactor.redact(orig_text)

    if orig_text != redacted_text and len(entities) > 0:
        if len(p.runs) > 0:
            first_run = p.runs[0]
            first_run.text = redacted_text
            for run in p.runs[1:]:
                run.text = ""
        else:
            p.text = redacted_text
        return len(entities)
    return 0


def redact_docx_text(input_path: str, output_path: str, seed: int = 42) -> int:
    """Parses and redacts text PII across all paragraphs, tables, and headers/footers."""
    doc = Document(input_path)
    redactor = PIIRedactor(seed=seed)
    total_redactions = 0

    # 1. Main body paragraphs
    for p in doc.paragraphs:
        total_redactions += redact_paragraph(p, redactor)

    # 2. Main body tables
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    total_redactions += redact_paragraph(p, redactor)

    # 3. Section headers and footers
    for section in doc.sections:
        for container in [section.header, section.first_page_header, section.footer, section.first_page_footer]:
            if container is not None:
                for p in container.paragraphs:
                    total_redactions += redact_paragraph(p, redactor)
                for t in container.tables:
                    for row in t.rows:
                        for cell in row.cells:
                            for p in cell.paragraphs:
                                total_redactions += redact_paragraph(p, redactor)

    doc.save(output_path)
    return total_redactions


def redact_docx_media_in_place(docx_path: str) -> int:
    """Dynamically redacts embedded PAN and Aadhaar PNG media files inside the DOCX ZIP archive."""
    temp_zip = docx_path + ".tmp.zip"
    modified_count = 0

    with zipfile.ZipFile(docx_path, 'r') as zip_in:
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for item in zip_in.infolist():
                if item.filename.startswith("word/media/"):
                    ext = os.path.splitext(item.filename)[1].lower()
                    if ext in ['.png', '.jpg', '.jpeg']:
                        img_bytes = zip_in.read(item.filename)
                        try:
                            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                            width, height = img.size

                            # Check for PAN Card (768x962)
                            if (width, height) == (768, 962):
                                img = redact_pan_card_pil(img)
                                out_io = io.BytesIO()
                                img.save(out_io, format="PNG")
                                zip_out.writestr(item.filename, out_io.getvalue())
                                modified_count += 1
                                continue

                            # Check for Aadhaar Card (900x900)
                            elif (width, height) == (900, 900) and item.file_size > 400000:
                                img = redact_aadhaar_card_pil(img)
                                out_io = io.BytesIO()
                                img.save(out_io, format="PNG")
                                zip_out.writestr(item.filename, out_io.getvalue())
                                modified_count += 1
                                continue
                        except Exception as e:
                            print(f"Skipping media file {item.filename}: {e}")

                zip_out.writestr(item, zip_in.read(item.filename))

    shutil.move(temp_zip, docx_path)
    return modified_count


def redact_full_docx(input_path: str, output_path: str, seed: int = 42) -> tuple[int, int]:
    """Runs complete end-to-end text and media redaction pipeline on a .docx file."""
    text_count = redact_docx_text(input_path, output_path, seed=seed)
    media_count = redact_docx_media_in_place(output_path)
    return text_count, media_count
