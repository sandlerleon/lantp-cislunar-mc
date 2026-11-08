# -*- coding: utf-8 -*-
"""Manuscript, part C: falsifiable conditions (7), discussion (8), conclusions (9), declarations, references."""
import math

from common import *

BEST = BM["best"]; POL = CT["policies"]; PK = list(POL.keys())
Zg = np.array(BE["ratio_mu_rho"], float); RHO = BE["rho"]; MU = BE["mu"]; Ns = np.array(BE["N_star"], float)
R50 = next(t["r50"] for t in BM["range_table"] if t["Dt"] == 10.0 and t["jit"] == 0.05)
R50J = next(t["r50"] for t in BM["range_table"] if t["Dt"] == 10.0 and t["jit"] == 0.3)
QO = OPT["q_ratio_opt"]; Zt = np.array(THR["ratio"], float); m1 = THR["mu_star_1"]; Pt = THR["P_use_GW"]
NT = [dict(best=min(x for x in r["M_ntp"] if x), ref=r["M_ntp"][1], lantp=r["M_lantp_10"]) for r in R["ntp_reactor"]["rows"]]

# ============================================================================================ 7 Falsifiable conditions
add(("h1", "7. Falsifiable conditions"))
add(("p", "The results of Section 6 can be stated as conditions that a laser-assisted tug must satisfy, each with the value this model gives (Table @T:claims@). They are conditional on the assumed ranges, and each is falsified by a single measurement or analysis that contradicts it. "
          "They also state where LANTP is inferior to conventional NTP: for a receiver specific mass above the threshold of Fig. @F:thr@, for payloads below several tens of tonnes, for a link that is interrupted or a node that is not held near the vehicle, and for any case in which the laser nodes are counted."))
rows = [["Specific impulse 1300–1500 s", "Useful laser power ≥ %s–%s × reactor power, and recovery of the dissociation energy in the nozzle" % (n(PW["rho_needed"]["1300"], 1), n(PW["rho_needed"]["1500"], 1)), "A 1–50 MW laser on 100–500 MWt gives ≤ %s s" % r100(max(PW["isp_at_claimed_laser"]))],
        ["Thrust 50–120 kN at 1400 s", "Emitted laser power %s–%s GW (median)" % (n(lt_at(1400, 50)[1] / 1e3, 1), n(lt_at(1400, 120)[1] / 1e3, 1)), "Short of the 1–50 MW class by a factor of %s–%s" % (n(lt_at(1400, 50)[1] / 50, 0), n(round(lt_at(1400, 120)[1] / 1.0, -2), 0))],
        ["Chamber temperature about 4500 K", "A heating and containment concept for a temperature above the highest measured melting temperature of a compound, 4232 ± 84 K (Table @T:mat@)", "Not demonstrated; not modeled"],
        ["Beam capture", "Captured fraction ≥ 0.5 only within %s km for a 10 m aperture, 0.05 µrad and a 3 m receiver; %s km at 0.3 µrad" % (r100(R50), r100(R50J)), "Relay beaming over 6×10⁴ km captures ≤ %s" % pc(BEST["L1_LLO"]["capture_max"], 0)],
        ["IMLEO 40% below conventional NTP", "Ratio ≤ 0.6 against a conventional tug with an optimized reactor", "Median %s; %s of draws below 1, %s at or below 0.6; best point of the map %s" % (n(QO[2], 2), pc(OPT["share_below_1"], 0), pc(OPT["share_below_06"], 0), n(float(np.nanmin(Zt)), 2))],
        ["Receiver specific mass", "Below the threshold of the map (Fig. @F:thr@)", "≤ %s kg/MW at %s GW, ≤ %s kg/MW at %s GW for any mass benefit" % (n(m1[0], 0), n(Pt[0], 2), n(m1[-1], 0), n(Pt[-1], 1))],
        ["Net benefit with infrastructure", "Spacecraft saving × missions ≥ node mass", "Median infrastructure-inclusive ratio %s; nodes %s t" % (n(np.nanmedian(RATIO_INF), 1), n(NOM["M_inf"] / 1e3, 0))],
        ["Continued mission after a laser fault", "Reserve propellant for reactor-only TLI", "Median ratio %s with the reserve (%s without)" % (n(POL[PK[1]]["q"][2], 2), n(POL[PK[0]]["q"][2], 2))]]
add(("table", "Table @T:claims@. Falsifiable conditions of a laser-assisted tug and the values of this model (all conditional on the assumed ranges).", ["Design target", "Condition", "This model"], rows, [1.9, 3.0, 2.4], 15))
rows = [["Reactor core outlet limit used in the model", "2600–2900 (2800 nominal)", "this paper"], ["Highest measured melting temperature of a compound, HfC$_{0.98}$", "4232 ± 84", "[@Cedillos2016]"],
        ["TaC–HfC system, range of measured melting temperatures", "4041–4232", "[@Cedillos2016]"], ["Graphite: melts only at 10–100 MPa", "4800 ± 100", "[@Savvatimskiy2005]"], ["Design chamber temperature of the targets", "4500", "targets"]]
add(("table", "Table @T:mat@. Temperatures (K) relevant to the 4500 K chamber. The melting temperatures are measured values from the cited studies as reported in their abstracts; graphite sublimes below the melting pressure.", ["Item", "Temperature (K)", "Source"], rows, [4.0, 1.7, 1.5]))

# ============================================================================================ 8 Discussion
add(("h1", "8. Discussion"))
add(("p", fmt("The three hypotheses are supported by the model under the assumed ranges. H1: the targeted specific impulse needs a useful laser power of <<r1>>–<<r2>> times the reactor power and the targeted thrust needs gigawatts of emitted laser power, not megawatts. H2: against a conventional tug with an optimized reactor the median IMLEO ratio is <<m>> and no draw reaches the targeted 0.6. "
              "H3: a mass benefit exists only below a receiver specific mass of <<a1>> to <<a2>> kg/MW (depending on the laser power) and then amounts to at most <<sv>> in the nominal case; it is lost when the infrastructure, a node that is not held near the vehicle or a laser fault is included. "
              "These conclusions are about the targets examined; they are not a general statement that laser power cannot assist nuclear thermal propulsion, and they depend on the receiver specific mass, which is the least certain input and the dominant one (Section 6.7).",
              r1=n(PW["rho_needed"]["1300"], 1), r2=n(PW["rho_needed"]["1500"], 1), m=n(QO[2], 2), a1=n(min(m for m in m1 if m), 0), a2=n(max(m for m in m1 if m), 0), sv=pc(1 - float(np.nanmin(Zt)), 0))))
add(("h2", "8.1 Relation to earlier work"))
add(("p", "Laser-heated hydrogen rockets, laser-sustained plasma thrusters and laser heat-exchanger rockets were analyzed and tested decades ago [@Kantrowitz1975;@Minovitch1972;@Kare1995;@Jeng1987;@Black1992;@Mertogul1990], and recent work continues on the thrust performance of laser heat-exchanger rockets and on the feasibility of laser thermal beamed-energy propulsion [@Mori2019;@McDonald2024]. "
          "Nuclear thermal tugs have been studied for cislunar transportation and compared with chemical propulsion [@Reynolds2019;@Reynolds2023;@Kumar2025;@Payton2025]. The contribution here is the coupling and the benchmark: the same model carries the thermodynamics of dissociating hydrogen, the power chain, the link along a finite burn, the mass of the receiver and of the laser nodes, "
          "and the policy for a laser outage, and compares the result with a conventional tug whose reactor is sized for the payload, so that the feasibility boundary is stated in quantities a designer can measure (laser power, receiver specific mass, captured fraction, number of missions). "
          "The literature was surveyed through bibliographic records, titles and abstracts; the full texts of the conference papers were not available to the author, so the comparison with earlier work is limited to what those records show."))
add(("h2", "8.2 What would change the conclusion"))
PLX = cross([p["m_pl"] / 1e3 for p in BE["payload"]], [p["ratio"] for p in BE["payload"]]); MUX = cross(MU, Zg[:, 2].tolist())
add(("p", fmt("The map identifies the levers. A receiver of a few kg/MW, a payload of several tens of tonnes, an infrastructure that already exists for another purpose (so that its mass is not charged to the transfers), a beam that is held for the whole burn by a node that stays close to the vehicle, and a nozzle that recovers most of the dissociation energy would together reduce the IMLEO. "
              "At 10 kg/MW the ratio against the 500 MWt reference tug falls below 1 for a payload above <<pl>> t, but against the best conventional tug only above about <<pl2>> t; with the nodes as an existing asset the break-even receiver mass at a laser fraction of 0.25 is approximately <<mc>> kg/MW. None of these conditions is demonstrated; each is a measurable target.",
              pl=n(PLX, 0) if PLX else "more than 80", pl2=n(40 + (NT[1]["lantp"] / NT[1]["best"] - 1) / (NT[1]["lantp"] / NT[1]["best"] - NT[2]["lantp"] / NT[2]["best"]) * 40, 0), mc=n(MUX, 0) if MUX else "below 2")))
add(("h2", "8.3 Limitations"))
add(("p", "(i) All design inputs (efficiencies, specific masses, link parameters, and coupling coefficients) are assumed ranges; they are not measurements and the results are conditional on them. (ii) The receiver specific mass is an assumed lumped parameter; the heating of the hydrogen to 4500 K without a solid wall at that temperature is not modeled, and the chamber temperature is a design target (Section 4.2). "
          "(iii) The thermodynamic model is a rigid-rotor, harmonic-oscillator model that overestimates the dissociation degree by 4–8% against Cantera; the nozzle is described by an expansion ratio, an efficiency and a recombination fraction, not by kinetics. (iv) The link assumes refocusing at every range, an ideal Gaussian beam and independent dropouts; atmospheric effects are absent and beam safety, acquisition and tracking are represented only by the reacquisition time. "
          "(v) The trajectory is coplanar with patched conics and thrust along the velocity, and the node is on a circular orbit phased near the vehicle; the result depends on that phasing (Section 6.5). (vi) The mass model is of design level, the infrastructure is a lower bound, and costs and the lifecycle are not modeled beyond the number of missions. "
          "(vii) The thermochemistry and the finite-burn integrator were verified independently, but the mission and mass model has a single implementation. (viii) The performance targets tested come from a concept description that is not in the open literature; they are treated as hypothetical design targets. "
          "(ix) The literature survey is limited to the bibliographic records, titles and abstracts available to the author."))

# ============================================================================================ 9 Conclusions
add(("h1", "9. Conclusions"))
add(("p", fmt("Within the assumed ranges, a laser of the targeted class cannot lift a nuclear thermal tug to the targeted performance: a useful laser power of <<r1>>–<<r2>> times the reactor power is needed for 1300–1500 s and gigawatts of emitted power for 50–120 kN. The beam can only act within a few 10$^4$ km of a node that is held near the vehicle, and the receiver and the reactor dominate the mass (Sobol total indices <<t1>> and <<t2>>). "
              "Against a conventional tug with an optimized reactor the median IMLEO ratio is <<m>> (5th–95th percentile <<q5>>–<<q95>>), with no draw at the targeted 0.6; the technology-threshold map shows that a mass benefit needs a receiver of less than approximately <<ms>> kg per MW absorbed and is at most <<sv>>. "
              "The laser nodes weigh <<mi>> kt for the nominal vehicle and a single laser fault costs propellant, which increases the median ratio at equal reactor power from <<c0>> to <<c1>>. The falsifiable conditions of Table @T:claims@ define what a demonstration would have to show: a receiver specific mass of a few kg/MW, a captured fraction above 0.5 over the whole burn, "
              "a heating concept for 4500 K that does not rely on a solid wall, a nozzle that recovers the dissociation energy, and an amortization of the nodes over many missions.",
              r1=n(PW["rho_needed"]["1300"], 1), r2=n(PW["rho_needed"]["1500"], 1), t1=n(SOB["ST"][SOB["keys"].index("mu_rec")], 2), t2=n(SOB["ST"][SOB["keys"].index("P_R")], 2), m=n(QO[2], 2), q5=n(QO[0], 2), q95=n(QO[4], 2), ms=n(max(m for m in m1 if m), 0), sv=pc(1 - float(np.nanmin(Zt)), 0),
              mi=n(NOM["M_inf"] / 1e6, 0), c0=n(POL[PK[0]]["q"][2], 1), c1=n(POL[PK[1]]["q"][2], 1))))

# ============================================================================================ declarations
add(("h1", "Declarations"))
add(("p0", "Funding: This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."))
add(("p0", "Competing interests: The author declares no competing interests."))
add(("p0", "Author contributions: Leon Sandler is the sole author: conceptualization, methodology, software, validation, formal analysis, investigation, visualization, writing – original draft, writing – review and editing."))
add(("p0", "Data and code availability: The simulation code, the data behind every figure and table, the automated tests and the manuscript sources (version %s) are archived at https://doi.org/%s (software, all versions) and https://doi.org/%s (manuscript, all versions), and are available at %s. The study uses no experimental data." % (VERSION, DOIS["code_concept"], DOIS["paper_concept"], GITHUB)))
add(("p0", "Use of AI tools: see Section 5.6. A generative AI tool (Claude, Anthropic) assisted with drafting text, writing and testing simulation code and generating figures from that code; the author reviewed and edited the content and takes full responsibility for it."))
add(("p0", "Ethics approval and consent: not applicable."))
add(("refs",))
