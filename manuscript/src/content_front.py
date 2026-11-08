# -*- coding: utf-8 -*-
"""Manuscript front matter: title, author, abstract, keywords (CEAS Space Journal)."""
from common import *

POL = CT["policies"]; PK = list(POL.keys())
QO = OPT["q_ratio_opt"]
mu1 = [m for m in THR["mu_star_1"] if m]
add(("title", TITLE))
add(("author", "Leon Sandler"))
add(("small", "Independent Researcher, Northbrook, Illinois, USA"))
add(("small", "ORCID: https://orcid.org/0009-0007-4584-808X"))
add(("small", "Corresponding author: " + EMAIL))
add(("blank",))
add(("h1", "Abstract"))
add(("p0", fmt("Laser-assisted nuclear thermal propulsion (LANTP) would raise the specific impulse of a nuclear thermal tug by adding orbital laser power to the hydrogen. We take performance targets of this kind (specific impulse 1300–1500 s, thrust 50–120 kN, a 1–50 MW laser on a 100–500 MWt reactor, and an initial mass in low Earth orbit, IMLEO, 40% below that of conventional nuclear thermal propulsion, NTP) as hypothetical design targets and test them for Earth–Moon logistics with a coupled model: "
               "hydrogen thermochemistry checked against Cantera, a power chain from the wall plug to the propellant, Gaussian-beam capture, finite burns with occultation and link dropouts, tug and laser-node masses, and Monte Carlo and Sobol analyses over assumed ranges. "
               "Reaching 1300–1500 s requires a useful laser power of <<r1>>–<<r2>> times the reactor power, so a 1–50 MW laser gives at most <<mx>> s, and 50–120 kN needs <<p50>>–<<p120>> GW of emitted power. Against a conventional tug whose reactor is sized for the payload, the laser-assisted tug has a median IMLEO ratio of <<m>> (5th–95th percentile <<q5>>–<<q95>>); <<b1>> of the draws are below 1 and none reaches 0.6. "
               "Receiver specific mass accounts for <<sv>> of the variance. A technology-threshold map shows that a mass benefit needs a receiver below approximately <<ms>> kg per MW absorbed. The laser nodes (about <<mi>> kt) and the propellant reserve for a single laser fault eliminate this benefit. Results are conditional on the assumed ranges.",
               r1=n(PW["rho_needed"]["1300"], 1), r2=n(PW["rho_needed"]["1500"], 1), mx=r100(max(PW["isp_at_claimed_laser"])), p50=n(lt_at(1400, 50)[1] / 1e3, 1), p120=n(lt_at(1400, 120)[1] / 1e3, 1),
               m=n(QO[2], 2), q5=n(QO[0], 2), q95=n(QO[4], 2), b1=pc(OPT["share_below_1"], 0), sv=pc([t for k, t in zip(SOB["keys"], SOB["ST"]) if k == "mu_rec"][0], 0), ms=n(max(mu1), 0), mi=n(NOM["M_inf"] / 1e6, 0))))
add(("p0", "Keywords: Laser-assisted nuclear thermal propulsion; Cislunar logistics; Beamed energy; Power closure; Monte Carlo simulation; Sobol sensitivity analysis"))
