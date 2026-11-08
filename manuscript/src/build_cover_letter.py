# -*- coding: utf-8 -*-
"""Cover letter for the submission to CEAS Space Journal (Springer); numbers from results/results.json, DOIs from dois.json.

    python build_cover_letter.py   -> manuscript/LANTP_Cover_Letter.docx
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
from docx.shared import Pt, Inches

from common import *

POL = CT["policies"]; PK = list(POL.keys())
Zg = np.array(BE["ratio_mu_rho"], float)
d = Document()
st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11); st.paragraph_format.space_after = Pt(8)
for s in d.sections:
    s.left_margin = s.right_margin = Inches(1.0); s.top_margin = s.bottom_margin = Inches(0.75)


def para(t, bold=False, after=None):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


para("Leon Sandler", True, 0)
for t in ("Independent Researcher", "Northbrook, Illinois, USA", EMAIL, "ORCID 0009-0007-4584-808X"):
    para(t, after=0)
para("")
para(datetime.date.today().strftime("%d %B %Y").lstrip("0"))
para("The Editor-in-Chief", after=0); para("CEAS Space Journal", after=0); para("Springer Nature")
para("Dear Editor,")
para("I submit the manuscript “%s” as an original research article for consideration in the CEAS Space Journal." % TITLE)
para("Laser-assisted nuclear thermal propulsion (LANTP) is proposed as a way to raise the specific impulse of a nuclear thermal tug for Earth–Moon logistics by adding orbital laser power to the hydrogen. Concepts of this kind are described with performance targets (specific impulse 1300–1500 s, thrust 50–120 kN, a laser of 1–50 MW on a 100–500 MWt reactor, "
     "and an initial mass in low Earth orbit 40% below that of conventional nuclear thermal propulsion). The targets come from a concept description that is not in the open literature, so the manuscript treats them as hypothetical design targets and tests them with a coupled model of the thermochemistry of dissociating hydrogen, the power chain from the electrical supply to the propellant, the optical link along finite burns with occultation and dropouts, "
     "the masses of the receiver and of the laser nodes, and the propellant reserve for laser outages. It quantifies the conditions under which the laser assistance is an advantage and those under which it is inferior to a conventional tug with an optimized reactor.")
para("The study is a space-transportation systems and feasibility analysis, not an experimentally validated propulsion technology. It establishes coupled feasibility boundaries for laser-assisted nuclear thermal propulsion in cislunar logistics, integrating thermochemistry, orbital laser transmission, spacecraft mass optimization, infrastructure requirements and operational contingencies. "
     "Rather than assuming a performance benefit, it identifies measurable technology thresholds that must be met for the architecture to outperform conventional nuclear thermal propulsion.")
para("The manuscript makes five contributions.(i) A hydrogen model checked against Cantera at identical conditions shows that a useful laser power of %s to %s times the reactor power is needed for 1300–1500 s, so that a 1–50 MW laser reaches at most about %s s, and that 50–120 kN needs gigawatts of emitted power. "
     "(ii) A beam-link and finite-burn analysis shows that the beam can act only within a few 10⁴ km of a node that is held near the vehicle. (iii) A Monte Carlo analysis with a conventional benchmark whose reactor is sized for the payload gives a median initial-mass ratio of %s (5th–95th percentile %s–%s) with no draw at the targeted 0.6, "
     "and Sobol indices identify the receiver specific mass and the reactor power as the dominant parameters. (iv) A technology-threshold map gives the receiver specific mass below which a mass benefit exists for any laser power (best case: %s). "
     "(v) Laser nodes of about %s kt and a propellant reserve for a single laser fault remove the benefit, and the paper states explicit, falsifiable conditions for the concept."
     % (n(PW["rho_needed"]["1300"], 1), n(PW["rho_needed"]["1500"], 1), r100(max(PW["isp_at_claimed_laser"])), n(OPT["q_ratio_opt"][2], 2), n(OPT["q_ratio_opt"][0], 2), n(OPT["q_ratio_opt"][4], 2), pc(1 - float(np.nanmin(np.array(THR["ratio"], float))), 0), n(NOM["M_inf"] / 1e6, 0)))
para("The study is explicit about what it is. Every design input is an assumed range, because no measurement of such a system exists; the heating of the hydrogen to 4500 K without a solid wall at that temperature is a design target that is not modeled; "
     "and the results are conditional on the assumed ranges and are not a general statement that laser power cannot assist nuclear thermal propulsion. The mission and mass model has a single implementation, while the thermochemistry and the finite-burn integrator were verified against independent solvers.")
para("The code, the data behind every figure and table, the tests and the manuscript sources are openly available at %s and archived at https://doi.org/%s (code, all versions); the manuscript and its Supplementary Information are archived at https://doi.org/%s "
     "(all versions). One command regenerates every number and figure." % (GITHUB, DOIS["code_concept"], DOIS["paper_concept"]))
para("Declarations. The work received no external funding and I have no competing interests.")
para("Author affiliation and email address. I am an independent researcher with no current institutional affiliation, and I am the sole author. The corresponding-author email address, %s, is my personal address." % EMAIL)
para("A generative AI tool (Claude, Anthropic) assisted with drafting text, writing and testing simulation code and generating figures from that code; I reviewed and edited all of it and take full responsibility for the content, as disclosed in the manuscript. "
     "The manuscript is original, has not been published elsewhere and is not under consideration at any other journal. I am the sole author.")
para("Thank you for considering this submission.")
para("Sincerely,")
para("Leon Sandler", True)
d.core_properties.title = "Cover letter: " + TITLE; d.core_properties.author = "Leon Sandler"
out = os.path.join(OUT, "LANTP_Cover_Letter.docx")
d.save(out)
print("saved", out)
