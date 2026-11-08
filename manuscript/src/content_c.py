# -*- coding: utf-8 -*-
"""Manuscript, part C: falsifiable conditions (7), asteroid extension (8), discussion (9), conclusions (10), declarations, references."""
import math

from common import *

BEST = BM["best"]; POL = CT["policies"]; PK = list(POL.keys())
Zg = np.array(BE["ratio_mu_rho"], float); RHO = BE["rho"]; MU = BE["mu"]; Ns = np.array(BE["N_star"], float)
R50 = next(t["r50"] for t in BM["range_table"] if t["Dt"] == 10.0 and t["jit"] == 0.05)
lp = AST["largest_diameter"]; Pg = AST["P_gw"]
D_ast = np.array(AST["main"]["D"]); q50 = np.array(AST["main"]["q50"]); q95 = np.array(AST["main"]["q95"])


def at_D(d, arr):
    return float(np.interp(math.log(d), np.log(D_ast), arr))



# ============================================================================================ 7 Falsifiable claims
add(("h1", "7. Falsifiable conditions"))
add(("p", "The results of Section 6 can be stated as conditions that the concept must satisfy, each with the value this model gives (Table @T:claims@). They are conditional on the assumed ranges, and each is falsified by a single measurement or analysis that contradicts it. "
          "They also state where LANTP is inferior to conventional NTP: for a receiver specific mass above a few kg/MW at the laser fractions of the claim, for small payloads, for a link that is interrupted, and for any case in which the laser nodes are counted."))
rows = [["Specific impulse 1300–1500 s", "Useful laser power ≥ %s–%s × reactor power, and recovery of the dissociation energy in the nozzle" % (n(PW["rho_needed"]["1300"], 1), n(PW["rho_needed"]["1500"], 1)), "A 1–50 MW laser on 100–500 MWt gives ≤ %s s" % r100(max(PW["isp_at_claimed_laser"]))],
        ["Thrust 50–120 kN at 1400 s", "Emitted laser power %s–%s GW (median)" % (n(lt_at(1400, 50)[1] / 1e3, 1), n(lt_at(1400, 120)[1] / 1e3, 1)), "Short of the 1–50 MW class by a factor of %s–%s" % (n(lt_at(1400, 50)[1] / 50, 0), n(round(lt_at(1400, 120)[1] / 1.0, -2), 0))],
        ["Chamber temperature about 4500 K", "A heating and containment concept that withstands a temperature above the highest reported melting temperatures of refractory solids (Table @T:mat@)", "Not demonstrated"],
        ["Beam capture", "Captured fraction ≥ 0.5 only within %s km for a 10 m aperture, 0.05 µrad and a 3 m receiver; %s km at 0.3 µrad" % (r100(R50), r100(next(t["r50"] for t in BM["range_table"] if t["Dt"] == 10.0 and t["jit"] == 0.3))), "Relay beaming over 6×10⁴ km captures ≤ %s" % pc(BEST["L1_LLO"]["capture_max"], 0)],
        ["IMLEO 40% below conventional NTP", "Ratio ≤ 0.6", "Median %s; %s of draws at or below 0.6; best grid point %s" % (n(RQ[2], 2), pc(SHARE_CLAIM, 0), n(float(np.nanmin(Zg)), 2))],
        ["Net benefit with infrastructure", "Spacecraft saving × missions ≥ node mass", "Median infrastructure-inclusive ratio %s; nodes %s t" % (n(np.nanmedian(RATIO_INF), 1), n(NOM["M_inf"] / 1e3, 0))],
        ["Continued mission after a laser fault", "Reserve propellant for reactor-only TLI", "Median ratio %s with the reserve" % n(POL[PK[1]]["q"][2], 2)]]
add(("table", "Table @T:claims@. Falsifiable conditions of the concept and the values of this model (all conditional on the assumed ranges).", ["Claim", "Condition", "This model"], rows, [1.9, 3.0, 2.4], 15))
rows = [["Reactor core limit used", "2600–2900 (2800 nominal)"], ["Tungsten, melting", "3695"], ["Graphite, sublimation at 1 atm", "about 3900"], ["TaC–HfC system, highest melting temperature reported [@Cedillos2016]", "about 4000"], ["Design chamber temperature of the claim", "4500"]]
add(("table", "Table @T:mat@. Temperatures (K) relevant to the 4500 K chamber (handbook values for the first three solids are quoted from memory of standard tables and should be verified).", ["Item", "Temperature (K)"], rows, [4.6, 1.7]))

# ============================================================================================ 8 Asteroid extension
add(("h1", "8. Extension: directed-energy deflection of an asteroid"))
add(("p", fmt("A beam of the power that LANTP would need could in principle also be used to deflect an asteroid [@Lubin2015]. A simple model tests this for the infrastructure above: the beam of <<P>> GW from a 10 m aperture reaches the asteroid at a range of 3×10$^4$–3×10$^5$ km, the spot size follows from the same optical model, "
              "the momentum coupling saturates at 30–300 µN/W with a half-saturation intensity of 10$^8$–10$^{10}$ W/m², and the irradiation lasts half of a lead time of 1–10 days; the displacement achieved at the Earth is divided by the required miss of one Earth radius. "
              "The median ratio is <<a40>> for a 40 m asteroid and <<a90>> for a 90 m asteroid (95th percentile <<b40>> and <<b90>>) (Fig. @F:ast@a), and the largest diameter that is deflected is <<d1>> m at 1.4 GW and <<d2>> m at 30 GW with a 10 m aperture (Fig. @F:ast@b). "
              "Even 30 GW deflects only asteroids up to about <<d3>> m with a 100 m aperture, below the 40–90 m class for most of it. The conclusion rests on the assumed coupling and lead time and is a limitation of the concept rather than a result of the transport analysis.",
              P="1.4", a40=sci(at_D(40, q50)), a90=sci(at_D(90, q50)), b40=sci(at_D(40, q95)), b90=sci(at_D(90, q95)), d1="less than 1" if float(np.interp(math.log(1.4), np.log(Pg), lp["10"])) < 1 else n(float(np.interp(math.log(1.4), np.log(Pg), lp["10"])), 0), d2=n(lp["10"][-1], 0), d3=n(lp["100"][-1], 0))))
add(("fig", "Fig13_asteroid.png", "Fig. @F:ast@. (a) Achieved over required displacement against asteroid diameter for 1.4 GW and a 10 m aperture (median and 5–95% band; shaded: 40–90 m class). (b) Largest diameter that is deflected against the emitted power for three apertures.", 6.2))

# ============================================================================================ 9 Discussion
add(("h1", "9. Discussion"))
add(("p", fmt("The three hypotheses are supported by the model under the assumed ranges. H1: the claimed specific impulse needs a useful laser power of <<r1>>–<<r2>> times the reactor power and the claimed thrust needs gigawatts of emitted laser power, not megawatts. H2: the median IMLEO is <<m>> times that of conventional NTP and no draw reaches the claimed 40% reduction. "
              "H3: a break-even region exists (ratio down to <<mn>>) only for the smallest receivers and low laser fractions, and it is lost when the infrastructure, the link or a laser fault is included. These conclusions are about the claims examined; they are not a general statement that laser power cannot assist nuclear thermal propulsion, "
              "and they depend on the receiver specific mass, which is the least certain input and the dominant one.",
              r1=n(PW["rho_needed"]["1300"], 1), r2=n(PW["rho_needed"]["1500"], 1), m=n(RQ[2], 1), mn=n(float(np.nanmin(Zg)), 2))))
add(("h2", "9.1 Novelty and relation to earlier work"))
add(("p", "Laser-heated hydrogen rockets were analyzed for launch and orbit transfer decades ago [@Minovitch1972;@Kare1995;@Mertogul1990], and nuclear thermal tugs have been studied for the Moon [@Reynolds2019]. The contribution here is the coupling: the same model carries the thermodynamics of dissociating hydrogen, the power chain, the link along a finite burn, "
          "the mass of the receiver and of the laser nodes, and the policy for a laser outage, so that the feasibility boundary is stated in terms of quantities a designer can measure (laser fraction, receiver specific mass, captured fraction, number of missions). "
          "An infrastructure-aware view, in which the nodes are amortized over repeated shuttle missions, and a reliability-aware view, in which the vehicle must complete the transfer after a laser fault, are not part of the earlier analyses cited here, to the extent that these were found; a complete literature search was not made."))
add(("h2", "9.2 What would change the conclusion"))
NT0 = [dict(best=min(x for x in r["M_ntp"] if x), ref=r["M_ntp"][1], lantp=r["M_lantp_10"]) for r in R["ntp_reactor"]["rows"]]
PLX = cross([p["m_pl"] / 1e3 for p in BE["payload"]], [p["ratio"] for p in BE["payload"]]); MUX = cross(MU, Zg[:, 2].tolist())
add(("p", fmt("The model identifies the levers. A receiver of a few kg/MW, a payload of several tens of tonnes, an infrastructure that already exists for another purpose (so that its mass is not charged to the transfers), a beam that is held for the whole burn by a node that stays close to the vehicle, and a nozzle that recovers most of the dissociation energy would together reduce the IMLEO. "
              "At 10 kg/MW the ratio falls below 1 for a payload above <<pl>> t against the 500 MWt reference tug (and above about <<pl2>> t against the best conventional tug), and with the nodes as an existing asset the break-even receiver mass at a laser fraction of 0.25 is about <<mc>> kg/MW. None of these conditions is demonstrated; each is a measurable target.",
              pl=n(PLX, 0) if PLX else "more than 80", pl2=n(cross([40, 80], [NT0[1]["lantp"] / NT0[1]["best"], NT0[2]["lantp"] / NT0[2]["best"]]) or 0, 0) if False else n(40 + (NT0[1]["lantp"] / NT0[1]["best"] - 1) / (NT0[1]["lantp"] / NT0[1]["best"] - NT0[2]["lantp"] / NT0[2]["best"]) * 40, 0), mc=n(MUX, 0) if MUX else "below 2")))
add(("h2", "9.3 Limitations"))
add(("p", "(i) All design inputs (efficiencies, specific masses, link parameters, coupling coefficients) are assumed ranges; the ranges are not measurements and the results are conditional on them. (ii) The thermodynamic model is a rigid-rotor, harmonic-oscillator model that overestimates the dissociation degree by 4–8% against Cantera; the nozzle is described by an expansion ratio, an efficiency and a recombination fraction, "
          "not by kinetics, and the heat transfer, wall temperature and radiation of a chamber at 4500 K are not modeled. (iii) The link assumes refocusing at every range, an ideal Gaussian beam and independent dropouts; atmospheric effects are absent and beam safety, acquisition and tracking are represented only by the re-acquisition time. "
          "(iv) The trajectory is coplanar with patched conics and thrust along the velocity, and the node is on a circular orbit near the vehicle. (v) The mass model is of design level, the infrastructure is a lower bound, and costs and the lifecycle are not modeled beyond the number of missions. "
          "(vi) The performance claims tested are those of the concept description; no source of that description is cited here and the tested values should be checked against it. (vii) The literature cited was checked for existence and bibliographic data, not read in full for each statement."))

# ============================================================================================ 10 Conclusions
add(("h1", "10. Conclusions"))
add(("p", fmt("Within the assumed ranges, a laser of the claimed class cannot lift a nuclear thermal tug to the claimed performance: a useful laser power of <<r1>>–<<r2>> times the reactor power is needed for 1300–1500 s and gigawatts of emitted power for 50–120 kN. The beam can only act within a few 10$^4$ km of a node, the receiver dominates the mass, "
              "and the median IMLEO is <<m>> times that of conventional NTP (5th–95th percentile <<q5>>–<<q95>>), with no draw at the claimed 0.6. The laser nodes weigh <<mi>> t for the nominal vehicle and a single laser fault costs propellant. "
              "A narrow break-even region (ratio down to <<mn>>) exists for small receivers and low laser fractions. The falsifiable conditions of Table @T:claims@ define what a demonstration would have to show: a receiver specific mass of a few kg/MW, a captured fraction above 0.5 over the whole burn, a heating concept for 4500 K, a nozzle that recovers the dissociation energy, "
              "and an amortization of the nodes over many missions.",
              r1=n(PW["rho_needed"]["1300"], 1), r2=n(PW["rho_needed"]["1500"], 1), m=n(RQ[2], 1), q5=n(RQ[0], 1), q95=n(RQ[4], 1), mi=n(NOM["M_inf"] / 1e3, 0), mn=n(float(np.nanmin(Zg)), 2))))

# ============================================================================================ declarations
add(("h1", "Declaration of competing interest"))
add(("p0", "The author declares no competing interests."))
add(("h1", "Funding"))
add(("p0", "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."))
add(("h1", "CRediT authorship contribution statement"))
add(("p0", "Leon Sandler: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Visualization, Writing – original draft, Writing – review and editing."))
add(("h1", "Data availability"))
add(("p0", "The simulation code, the data behind every figure and table, the automated tests and the manuscript sources (version %s) are archived at https://doi.org/%s (software, all versions) and https://doi.org/%s (manuscript, all versions), and are available at %s. The study uses no experimental data." % (VERSION, DOIS["code_concept"], DOIS["paper_concept"], GITHUB)))
add(("h1", "Declaration of generative AI and AI-assisted technologies in the writing process"))
add(("p0", "During the preparation of this work the author used Claude (Anthropic) to assist with drafting text, writing and testing simulation code and generating figures from that code. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the publication."))
add(("refs",))
