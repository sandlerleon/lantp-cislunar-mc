# -*- coding: utf-8 -*-
"""Cover letter for the submission to Aerospace Science and Technology (Elsevier); numbers from results/results.json, DOIs from dois.json.

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
para("The Editor-in-Chief", after=0); para("Aerospace Science and Technology", after=0); para("Elsevier")
para("Dear Editor,")
para("I submit the manuscript “%s” as a research article for consideration in Aerospace Science and Technology." % TITLE)
para("Laser-assisted nuclear thermal propulsion (LANTP) is proposed as a way to raise the specific impulse of a nuclear thermal tug for Earth–Moon logistics by adding orbital laser power to the hydrogen. The performance claimed for such concepts (specific impulse 1300–1500 s, thrust 50–120 kN, a laser of 1–50 MW on a 100–500 MWt reactor, "
     "and 40% lower initial mass in low Earth orbit than conventional nuclear thermal propulsion) has not been tested against a coupled model. The manuscript does so with a model in which the thermochemistry of dissociating hydrogen, the power chain from the electrical supply to the propellant, the optical link along finite burns with occultation and dropouts, "
     "the mass of the receiver and of the laser nodes, and the propellant reserve for laser outages are solved together, and it quantifies the conditions under which the laser assistance is an advantage and those under which it is inferior to conventional NTP.")
para("The manuscript makes four contributions to the aerospace-propulsion literature. (i) A validated hydrogen model (checked against Cantera) shows that a useful laser power of %s to %s times the reactor power is needed for 1300–1500 s, so that a 1–50 MW laser reaches at most about %s s, and that 50–120 kN needs gigawatts of emitted power. "
     "(ii) A beam-link and finite-burn analysis shows that the beam can act only within a few 10⁴ km of a node and that relay beaming over the Earth–Moon distances is excluded. (iii) A Monte Carlo analysis over assumed ranges gives a median initial mass %s times that of conventional NTP (5th–95th percentile %s–%s), with none of the draws at the claimed 0.6, "
     "the receiver specific mass as the dominant parameter, a narrow break-even region (best ratio %s) and laser nodes whose mass exceeds that of the tug by orders of magnitude. (iv) A contingency analysis shows that carrying the propellant to complete the transfer after a single laser fault raises the median ratio to %s, and the paper states a set of explicit, falsifiable conditions for the concept."
     % (n(PW["rho_needed"]["1300"], 1), n(PW["rho_needed"]["1500"], 1), r100(max(PW["isp_at_claimed_laser"])), n(RQ[2], 1), n(RQ[0], 1), n(RQ[4], 1), n(float(np.nanmin(Zg)), 2), n(POL[PK[1]]["q"][2], 1)))
para("The study is explicit about what it is. Every design input is an assumed range, because no measurement of such a system exists; the performance claims tested are those of the concept description, which the manuscript does not cite and which should be checked; "
     "and the results are conditional on the assumed ranges and are not a general statement that laser power cannot assist nuclear thermal propulsion.")
para("The code, the data behind every figure and table, the tests and the manuscript sources are openly available at %s and archived at https://doi.org/%s (code, all versions); the manuscript and its Supplementary Information are archived at https://doi.org/%s "
     "(all versions). One command regenerates every number and figure." % (GITHUB, DOIS["code_concept"], DOIS["paper_concept"]))
para("Disclosure. The work received no external funding and I have no competing interests.")
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
