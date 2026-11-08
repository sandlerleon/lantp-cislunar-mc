# -*- coding: utf-8 -*-
"""Manuscript front matter: title, author, highlights, abstract, keywords."""
from common import *

POL = CT["policies"]; PK = list(POL.keys())
add(("title", TITLE))
add(("author", "Leon Sandler"))
add(("small", "Independent Researcher, Northbrook, Illinois, USA"))
add(("small", "ORCID: https://orcid.org/0009-0007-4584-808X"))
add(("small", "Corresponding author: " + EMAIL))
add(("blank",))
add(("h1", "Highlights"))
HIGH = [
    "Reaching 1300-1500 s needs laser power of %s-%s times the reactor power" % (n(PW["rho_needed"]["1300"], 1), n(PW["rho_needed"]["1500"], 1)),
    "A 1-50 MW laser on a 100-500 MWt reactor gives at most %s s" % r100(max(PW["isp_at_claimed_laser"])),
    "Median IMLEO is %s times that of conventional NTP; %s of draws reach -40%%" % (n(RQ[2], 1), pc(SHARE_CLAIM, 0)),
    "Beam capture collapses beyond a few 10^4 km, ruling out relay beaming",
    "Laser nodes outweigh the tug and a single laser fault erodes the benefit",
]
for h in HIGH:
    assert len(h) <= 85, (len(h), h)
    add(("bullet", h))
add(("h1", "Abstract"))
add(("p0", fmt("Laser-assisted nuclear thermal propulsion (LANTP) proposes to lift the specific impulse of a nuclear thermal tug by adding orbital laser power to the hydrogen, for logistics between low Earth orbit and low lunar orbit. We test the claims of such a concept (specific impulse 1300–1500 s, thrust 50–120 kN, a laser of 1–50 MW on a 100–500 MWt reactor, 40% lower initial mass in low Earth orbit, IMLEO) with a coupled model: hydrogen dissociation thermodynamics validated against Cantera, a power chain from wall plug to propellant, "
               "Gaussian-beam capture with pointing jitter, finite burns with occultation and link dropouts, a mass model of the tug and its laser nodes, and a Monte Carlo analysis over assumed ranges. A reactor-limited core gives <<ntp>> s; reaching 1300–1500 s needs useful laser power of <<r1>>–<<r2>> times the reactor power, so a 1–50 MW laser reaches at most <<mx>> s, and thrusts of 50–120 kN need emitted laser power of <<p50>>–<<p120>> GW at 1400 s. "
               "Median IMLEO is <<m>> times that of conventional nuclear thermal propulsion (5th–95th percentile <<q5>>–<<q95>>), none of the draws reaches the claimed 40% reduction, and receiver specific mass dominates (rank correlation <<sr>>). The laser nodes outweigh the tug by orders of magnitude, a single laser fault raises the median IMLEO ratio to <<c1>>, and a 1.4 GW beam falls short of deflecting a 40–90 m asteroid by more than two orders of magnitude. "
               "All inputs are assumed; the study gives falsification boundaries, not a design.",
               ntp=r10(PW["isp_ntp"][1]), r1=n(PW["rho_needed"]["1300"], 1), r2=n(PW["rho_needed"]["1500"], 1), mx=r100(max(PW["isp_at_claimed_laser"])), p50=n(lt_at(1400, 50)[1] / 1e3, 1), p120=n(lt_at(1400, 120)[1] / 1e3, 1),
               m=n(RQ[2], 1), q5=n(RQ[0], 1), q95=n(RQ[4], 1), sr=n([r["rho"] for r in SENS if r["key"] == "mu_rec"][0], 2), c1=n(POL[PK[1]]["q"][2], 1))))
add(("p0", "Keywords: Laser-assisted nuclear thermal propulsion; cislunar logistics; power closure; Monte Carlo; beam capture; hydrogen dissociation"))
