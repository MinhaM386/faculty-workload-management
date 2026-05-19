#!/usr/bin/env python3
"""Generate a simple editable DOCX from the project report markdown source."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Faculty_Workload_Management_System_Report.md"
OUTPUT = ROOT / "Faculty_Workload_Management_System_Report.docx"


def para_xml(text: str, *, bold: bool = False, center: bool = False) -> str:
    safe = escape(text)
    justification = "<w:jc w:val=\"center\"/>" if center else ""
    run_props = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return (
        "<w:p>"
        f"<w:pPr>{justification}</w:pPr>"
        "<w:r>"
        f"{run_props}"
        f"<w:t xml:space=\"preserve\">{safe}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def blank_para() -> str:
    return "<w:p/>"


def markdown_to_document_xml(markdown_text: str) -> str:
    body_parts: list[str] = []

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            body_parts.append(blank_para())
            continue

        if line.strip() == "---":
            body_parts.append(blank_para())
            body_parts.append(para_xml("_" * 70, center=True))
            body_parts.append(blank_para())
            continue

        if line.startswith("# "):
            body_parts.append(blank_para())
            body_parts.append(para_xml(line[2:].strip(), bold=True, center=True))
            body_parts.append(blank_para())
            continue

        if line.startswith("## "):
            body_parts.append(blank_para())
            body_parts.append(para_xml(line[3:].strip(), bold=True))
            continue

        if line.startswith("### "):
            body_parts.append(para_xml(line[4:].strip(), bold=True))
            continue

        if line.startswith("- "):
            body_parts.append(para_xml(f"• {line[2:].strip()}"))
            continue

        if line[:3] in {"1. ", "2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. ", "9. "}:
            body_parts.append(para_xml(line))
            continue

        if line.startswith("|") and line.endswith("|"):
            cell_text = "   ".join(part.strip() for part in line.strip("|").split("|"))
            body_parts.append(para_xml(cell_text))
            continue

        cleaned = line.replace("`", "")
        body_parts.append(para_xml(cleaned))

    body_parts.append(
        "<w:sectPr>"
        "<w:pgSz w:w=\"12240\" w:h=\"15840\"/>"
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" "
        "w:header=\"708\" w:footer=\"708\" w:gutter=\"0\"/>"
        "</w:sectPr>"
    )

    body_xml = "".join(body_parts)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/word/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" "
        "mc:Ignorable=\"w14 wp14\">"
        f"<w:body>{body_xml}</w:body>"
        "</w:document>"
    )


def build_docx() -> None:
    markdown_text = SOURCE.read_text(encoding="utf-8")
    document_xml = markdown_to_document_xml(markdown_text)
    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Faculty Workload Management System Report</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>
</cp:coreProperties>
"""

    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Microsoft Office Word</Application>
</Properties>
"""

    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", content_types)
        docx.writestr("_rels/.rels", rels)
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("docProps/core.xml", core)
        docx.writestr("docProps/app.xml", app)


if __name__ == "__main__":
    build_docx()
    print(f"Created {OUTPUT}")
