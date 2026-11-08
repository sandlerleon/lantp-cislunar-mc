# -*- coding: utf-8 -*-
"""Separate title page with the author details and declarations (Springer layout assumed; the current CEAS Space Journal guide for authors was not retrieved and must be checked before upload).

    python build_submission_files.py   -> manuscript/LANTP_Title_Page.docx
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt, Inches

from common import *


def new_doc():
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(6)
    for s in d.sections:
        s.left_margin = s.right_margin = Inches(1.0); s.top_margin = s.bottom_margin = Inches(0.9)
    return d


d = new_doc()
p = d.add_paragraph(); r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(14)
d.add_paragraph("Leon Sandler")
d.add_paragraph("Independent Researcher, Northbrook, Illinois, USA")
d.add_paragraph("ORCID: https://orcid.org/0009-0007-4584-808X")
d.add_paragraph("Corresponding author: Leon Sandler, " + EMAIL)
for t in ("Author contributions (CRediT): Leon Sandler, sole author: conceptualization, methodology, software, validation, formal analysis, investigation, visualization, writing – original draft, writing – review and editing.",
          "Funding: This work received no external funding.",
          "Declaration of competing interest: the author declares no competing interests.",
          "Declaration of generative AI and AI-assisted technologies in the writing process: a generative AI tool (Claude, Anthropic) assisted with drafting text, writing and testing simulation code and generating figures from that code. The author reviewed and edited the content as needed and takes full responsibility for the content.",
          "Data and code availability: the code, the data of every figure and table, the tests and the manuscript are archived at https://doi.org/%s (software, all versions) and https://doi.org/%s (manuscript, all versions), and are available at %s." % (DOIS["code_concept"], DOIS["paper_concept"], GITHUB)):
    d.add_paragraph(t)
d.core_properties.title = "Title page: " + TITLE; d.core_properties.author = "Leon Sandler"
d.save(os.path.join(OUT, "LANTP_Title_Page.docx"))
print("saved title page")
