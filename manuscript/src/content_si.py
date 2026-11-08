# -*- coding: utf-8 -*-
"""Supplementary information."""
import math

from common import *

Zg = np.array(BE["ratio_mu_rho"], float); Ns = np.array(BE["N_star"], float)

adds(("title", "Supplementary Information"))
adds(("small", TITLE))
adds(("author", "Leon Sandler"))
adds(("small", "Independent Researcher, Northbrook, Illinois, USA. " + EMAIL))
adds(("blank",))

adds(("h1", "S1. Thermochemistry"))
rows = [[n(a["T"], 0), n(a["p"] / 1e6, 1), n(a["ref"], 4), n(a["mine"], 4), pc(a["mine"] / a["ref"] - 1, 1)] for a in VAL["alpha"]]
adds(("table", "Table S1. Dissociation degree of hydrogen: this model and %s." % VAL.get("tool", "Cantera"), ["T (K)", "p (MPa)", "Reference", "This model", "Difference"], rows, [1.0, 1.0, 1.2, 1.2, 1.2]))
rows = [[g["T"], n(g["p"] / 1e6, 1), n(g["gibbs"], 6), n(g["analytic"], 6)] for g in VAL["gibbs"]]
adds(("table", "Table S2. Dissociation degree from a numerical minimization of the Gibbs energy and from the analytic equilibrium constant (same thermodynamic data).", ["T (K)", "p (MPa)", "Gibbs minimization", "Analytic"], rows, [1.0, 1.0, 1.5, 1.5]))

adds(("h1", "S2. Power and laser"))
rows = []
for F in (20, 50, 80, 120, 150):
    r = [str(F)]
    for tg in (1300, 1400, 1500):
        v = lt_at(tg, F); r.append("%s (%s–%s)" % (n(v[1], 0), n(v[0], 0), n(v[2], 0)))
    rows.append(r)
adds(("table", "Table S3. Emitted laser power (MW; median and 5th–95th percentile) for a given thrust and target specific impulse (start of the burn, full capture).", ["Thrust (kN)", "1300 s", "1400 s", "1500 s"], rows, [1.0, 1.7, 1.7, 1.7]))
rows = [[n(t["Dt"], 0), n(t["jit"], 2), n(t["r50"], 0) if t["r50"] else "–", n(t["r10"], 0) if t["r10"] else "–"] for t in BM["range_table"]]
adds(("table", "Table S4. Range (km) at which the captured fraction falls to 0.5 and 0.1 for a 3 m receiver, $M^2$ = 1.2.", ["Aperture (m)", "Jitter (µrad)", "Range at 0.5", "Range at 0.1"], rows, [1.2, 1.2, 1.4, 1.4]))
rows = [[k.replace("_", " "), n(v["R_km"], 0), n(v["capture_10m"], 3), n(v["capture_100m"], 3), n(v["capture_max"], 3), n(v["Dt_for_half"], 1) if v["Dt_for_half"] else "none", n(v["r_R_for_half_10m"], 1) if v["r_R_for_half_10m"] else "none"] for k, v in BM["best"].items()]
adds(("table", "Table S5. Captured fraction at the ranges of the burns and relay links (0.05 µrad jitter).", ["Segment", "Range (km)", "10 m aperture", "100 m aperture", "Best", "Aperture for 0.5 (m)", "Receiver radius for 0.5, 10 m aperture (m)"], rows, [1.2, 0.9, 0.9, 0.9, 0.7, 1.0, 1.2], 14))

adds(("h1", "S3. Mission studies"))
rows = [[n(r["rho"], 2), "%s–%s" % (n(r["q"][0], 2), n(r["q"][2], 2)), n(r["q"][1], 2), n(r["Isp_med"], 0), pc(r["feasible"], 0)] for r in RR["rows"]]
adds(("table", "Table S6. IMLEO ratio against the useful laser power fraction (5–95%, median), median specific impulse and share of draws that close.", ["Fraction", "5–95%", "Median", "Median Isp (s)", "Closed"], rows, [1.0, 1.5, 1.0, 1.2, 1.0]))
rows = [[n(m_, 0), n(RM["design"][i]["q"][1], 2), "%s–%s" % (n(RM["design"][i]["q"][0], 2), n(RM["design"][i]["q"][2], 2)), n(RM["rho025"][i]["q"][1], 2), "%s–%s" % (n(RM["rho025"][i]["q"][0], 2), n(RM["rho025"][i]["q"][2], 2))] for i, m_ in enumerate(RM["mu"])]
adds(("table", "Table S7. IMLEO ratio against the receiver specific mass: median and interquartile range for the 4500 K design and for a laser fraction of 0.25.", ["Receiver (kg/MW)", "Design, median", "Design, IQR", "0.25, median", "0.25, IQR"], rows, [1.2, 1.2, 1.5, 1.2, 1.5]))
hdr = ["Receiver (kg/MW)"] + ["ρ = %g" % r_ for r_ in BE["rho"]]
rows = [[n(m_, 0)] + [n(Zg[i, j], 2) for j in range(len(BE["rho"]))] for i, m_ in enumerate(BE["mu"])]
adds(("table", "Table S8. IMLEO ratio of the nominal vehicle on the grid of receiver specific mass and useful laser power fraction ρ.", hdr, rows, [1.3] + [0.7] * len(BE["rho"]), 14))
rows = [[n(m_, 0)] + [("none" if not np.isfinite(Ns[i, j]) else n(Ns[i, j], 0)) for j in range(len(BE["rho"]))] for i, m_ in enumerate(BE["mu"])]
adds(("table", "Table S9. Number of missions over which the laser nodes must be amortized for the spacecraft saving to equal the node mass (none: LANTP is heavier than conventional NTP).", hdr, rows, [1.3] + [0.7] * len(BE["rho"]), 14))
rows = [[n(t["tof"], 1), n(t["dv"], 2), n(t["t_tli"] / 60, 0), n(t["ratio"], 2)] for t in BE["tof"]]
adds(("table", "Table S10. Transfer time: total impulsive Δv (TLI + LOI, km/s), TLI burn time and IMLEO ratio of the nominal vehicle (receiver 10 kg/MW).", ["Time of flight (d)", "Δv (km/s)", "TLI burn (min)", "IMLEO ratio"], rows, [1.4, 1.2, 1.3, 1.2]))
rows = [[n(p["m_pl"] / 1e3, 0), n(p["M_ntp"] / 1e3, 0), n(p["M_lantp"] / 1e3, 0), n(p["ratio"], 2)] for p in BE["payload"]]
adds(("table", "Table S11. Payload: initial masses and ratio (receiver 10 kg/MW).", ["Payload (t)", "NTP (t)", "LANTP (t)", "Ratio"], rows, [1.2, 1.2, 1.2, 1.2]))
rows = [[r["name"].replace("$", ""), n(r["rho"], 3)] for r in sorted(SENS, key=lambda r: -abs(r["rho"]))]
adds(("table", "Table S12. Spearman rank correlation of the IMLEO ratio with the uncertain parameters.", ["Parameter", "Correlation"], rows, [3.4, 1.4]))
rows = [[k, n(v["q"][0], 2), n(v["q"][1], 2), n(v["q"][2], 2), n(v["q"][3], 2), n(v["q"][4], 2), n(v["feasible"], 2)] for k, v in CT["policies"].items()]
adds(("table", "Table S13. Contingency policies: IMLEO ratio percentiles (5, 25, 50, 75, 95) and share of draws that close.", ["Policy", "5%", "25%", "50%", "75%", "95%", "Closed"], rows, [3.0, 0.7, 0.7, 0.7, 0.7, 0.7, 0.8], 14))
rows = [[n(o["t_out_frac"], 2), n(o["burned_t"], 1), n(o["t_burn_min"], 0)] for o in CT["outage_curve"]]
adds(("table", "Table S14. TLI burn of the nominal vehicle after a loss of the laser at a fraction of the nominal burn time: propellant and burn time.", ["Fraction of burn", "Propellant (t)", "Burn time (min)"], rows, [1.4, 1.4, 1.4]))
RT = R.get("roundtrip", {}).get("rows", [])
if RT:
    rows = [[n(r["m_pl"] / 1e3, 0), n(r["mu"], 0), n(r["M_ntp"] / 1e3, 0) if r["M_ntp"] else "no closure", n(r["M_lantp"] / 1e3, 0) if r["M_lantp"] else "no closure", n(r["ratio"], 2) if r["ratio"] else "–"] for r in RT]
    adds(("table", "Table S15. Round trip with propulsive return (four burns, reusable tug), nominal vehicle.", ["Payload (t)", "Receiver (kg/MW)", "NTP (t)", "LANTP (t)", "Ratio"], rows, [1.1, 1.3, 1.1, 1.1, 1.0]))
pv = [[k, n(np.nanpercentile(v, 5), 2), n(np.nanpercentile(v, 50), 2), n(np.nanpercentile(v, 95), 2)] for k, v in (("Isp at 4500 K design (s)", ISPD), ("Effective Isp of TLI (s)", ISPE), ("IMLEO ratio", RATIO), ("IMLEO ratio with infrastructure", RATIO_INF), ("Emitted laser power (GW)", PEMIT), ("Electrical power at the node (GW)", PELEC), ("Infrastructure mass (t)", MINF))]
adds(("table", "Table S16. Percentiles of the main Monte Carlo outputs (%s draws)." % n(MC["n"]), ["Output", "5th", "50th", "95th"], pv, [3.2, 1.0, 1.0, 1.0]))

adds(("h1", "S4. Studies added in versions 1.1.0 and 1.2.0"))
rows = [["Isp frozen" if k == "f" else "Isp shifting", "%g K, %g MPa" % (i["Tc"], i["p_c"] / 1e6), n(i["frozen_ref" if k == "f" else "shifting_ref"], 0), n(i["frozen_mine" if k == "f" else "shifting_mine"], 0), n(i["frozen_ref94" if k == "f" else "shifting_ref94"], 0), n(i["frozen_mine94" if k == "f" else "shifting_mine94"], 0)] for k in ("f", "s") for i in VAL["isp"]]
adds(("table", "Table S17. Specific impulse (s) of Cantera and of this model at the nozzle efficiency of 1 and of 0.94 (identical temperature, pressure and expansion ratio).", ["Quantity", "Condition", "Cantera, $η_n$ = 1", "This model, $η_n$ = 1", "Cantera × 0.94", "This model, $η_n$ = 0.94"], rows, [1.3, 1.5, 1.0, 1.0, 1.0, 1.0], 14))
rows = [[n(r["offset_km"], 0), n(r["ratio"], 2), n(r["M"] / 1e3, 0), n(r["t_tli_min"], 0), n(r["R_max_km"], 0), n(r["occulted_min"], 1), n(r["isp_min"], 0)] for r in NOFF["rows"]]
adds(("table", "Table S18. Phasing of the laser node: initial separation between node and vehicle, IMLEO ratio at equal reactor power, initial mass, TLI burn time, largest node–vehicle range during TLI, time with the line of sight blocked during TLI, and lowest instantaneous specific impulse (nominal vehicle).", ["Separation (km)", "Ratio", "Mass (t)", "TLI (min)", "Max range (km)", "Occulted (min)", "Min Isp (s)"], rows, [1.1, 0.7, 0.8, 0.8, 1.0, 1.0, 0.9], 14))
rows = [[r["burn"], n(r["M"] / 1e3, 0), n(r["propellant_independent"], 0), n(r["propellant_model"], 0), pc(r["diff"], 2), n(r["t_independent"], 0), n(r["t_model"], 0)] for r in IBURN["rows"]]
rows += [[r["burn"] + ", limiting case", n(r["M"] / 1e3, 0), n(r["propellant_rocket_equation"], 0), n(r["propellant_model"], 0), pc(r["diff"], 2), "–", "–"] for r in IBURN["limit"]]
adds(("table", "Table S19. Checks of the finite-burn integration. Rows 1–6: independent integration (adaptive DOP853) and mission-model integration (fixed step) of the same equations with constant specific impulse: propellant (kg), difference and burn time (s); this verifies the numerical accuracy only. Rows 7–12 (limiting case): near-impulsive burn of the mission model (thrust 40 times the nominal) against the rocket equation with the impulsive velocity change of the transfer (the column 'independent' then holds the rocket-equation propellant).", ["Burn", "Mass (t)", "Propellant, independent", "Propellant, model", "Difference", "Time, independent", "Time, model"], rows, [1.7, 0.7, 1.1, 1.0, 0.8, 0.9, 0.8], 14))
SL = SOB["log"]
rows = [[nm_, n(a, 3), "%s–%s" % (n(a1, 3), n(a2, 3)), n(b, 3), "%s–%s" % (n(lo, 3), n(hi, 3)), n(l1, 3), n(lt, 3)] for nm_, a, a1, a2, b, lo, hi, l1, lt in sorted(zip(SOB["names"], SOB["S1"], SOB["S1_lo"], SOB["S1_hi"], SOB["ST"], SOB["ST_lo"], SOB["ST_hi"], SL["S1"], SL["ST"]), key=lambda t: -t[4])]
adds(("table", "Table S20. Sobol indices of the IMLEO ratio at equal reactor power (base sample %s, %s model evaluations, scrambled Sobol sequence): first-order index and total index, each with its 95%% bootstrap interval, and the same indices for the logarithm of the ratio (last two columns)." % (n(SOB["N"]), n(SOB["evaluations"])), ["Parameter", "First-order", "First-order, 95% interval", "Total", "Total, 95% interval", "First-order (log)", "Total (log)"], rows, [1.8, 0.8, 1.2, 0.8, 1.2, 0.8, 0.8]))
rows = [[n(r_, 2), n(P_, 2), n(t_, 0), n(a_, 1) if a_ else "–", n(b_, 1) if b_ else "–"] for r_, P_, t_, a_, b_ in zip(THR["rho"], THR["P_use_GW"], THR["Tc"], THR["mu_star_1"], THR["mu_star_0.9"])]
adds(("table", "Table S21. Technology-threshold map: laser fraction, useful laser power (reactor 500 MWt), chamber temperature at that power, and the receiver specific mass (kg/MW) below which the IMLEO ratio is below 1 and below 0.9 (– : not reached down to 1 kg/MW).", ["Laser fraction", "Useful power (GW)", "Chamber T (K)", "Receiver for ratio < 1", "Receiver for ratio < 0.9"], rows, [1.1, 1.2, 1.1, 1.3, 1.3]))
rows = [["median", n(OPT["q_ratio_opt"][2], 2), n(OPT["q_ratio_claim_reactor"][2], 2)], ["5th percentile", n(OPT["q_ratio_opt"][0], 2), n(OPT["q_ratio_claim_reactor"][0], 2)], ["25th percentile", n(OPT["q_ratio_opt"][1], 2), n(OPT["q_ratio_claim_reactor"][1], 2)],
        ["75th percentile", n(OPT["q_ratio_opt"][3], 2), n(OPT["q_ratio_claim_reactor"][3], 2)], ["95th percentile", n(OPT["q_ratio_opt"][4], 2), n(OPT["q_ratio_claim_reactor"][4], 2)]]
adds(("table", "Table S22. IMLEO ratio against the conventional tug with an optimized reactor (%s draws): both tugs optimized, and the laser-assisted tug at the reactor power of the draw." % n(OPT["n"]), ["Statistic", "Both optimized", "LANTP at the reactor of the draw"], rows, [1.8, 1.5, 2.2]))

if SCAL:
    rows = [[n(r["exp"], 1), n(r["q_ratio_opt"][2], 2), "%s–%s" % (n(r["q_ratio_opt"][0], 2), n(r["q_ratio_opt"][4], 2)), pc(r["share_below_1"], 0), n(r["P_ntp_median"], 0), n(r["P_lantp_median"], 0), n(r["M_ntp_median"] / 1e3, 1), n(r["M_lantp_median"] / 1e3, 1)] for r in SCAL["rows"]]
    adds(("table", "Table S23. Scaling of the engine-system mass with reactor power ($P_R^{x}$ at constant thrust, relative to 500 MWt) in the optimized benchmark (%s draws): median IMLEO ratio and 5th–95th percentile, share of draws below 1, median optimal reactor power (MWt) of the conventional and of the laser-assisted tug, and median initial masses (t)." % n(SCAL["n"]), ["Exponent x", "Median ratio", "5th–95th", "Below 1", "Optimal P, NTP", "Optimal P, LANTP", "M, NTP (t)", "M, LANTP (t)"], rows, [0.8, 0.9, 1.0, 0.7, 0.9, 0.9, 0.8, 0.9]))

cv = SOB["convergence"]; ks = list(cv.keys()); i_mu = SOB["keys"].index("mu_rec"); i_P = SOB["keys"].index("P_R")
rows = [[k_, n(cv[k_]["S1"][i_mu], 3), n(cv[k_]["ST"][i_mu], 3), n(cv[k_]["S1"][i_P], 3), n(cv[k_]["ST"][i_P], 3)] for k_ in ks]
adds(("table", "Table S24. Convergence of the Sobol indices of the receiver specific mass and of the reactor power with the base sample size.", ["Base sample", "Receiver: first-order", "Receiver: total", "Reactor: first-order", "Reactor: total"], rows, [1.2, 1.2, 1.2, 1.2, 1.2]))

adds(("h1", "S5. Directed-energy deflection of an asteroid (illustrative extension)"))
D_ast = np.array(AST["main"]["D"]); q50_ = np.array(AST["main"]["q50"]); q95_ = np.array(AST["main"]["q95"]); lp_ = AST["largest_diameter"]; Pg_ = AST["P_gw"]
adds(("p", fmt("A beam of the power that LANTP would need could in principle also be used to deflect an asteroid [@Lubin2015]. A simple model, given as an illustration and not as a result of the transport analysis: the beam of 1.4 GW from a 10 m aperture reaches the asteroid at a range of 3×10$^4$–3×10$^5$ km, the spot size follows from the optical model of Section 4.1, the momentum coupling saturates at 30–300 µN/W with a half-saturation intensity of 10$^8$–10$^{10}$ W/m², "
               "and the irradiation lasts half of a lead time of 1–10 days; the displacement achieved at the Earth is divided by the required miss of one Earth radius. The median ratio is <<a40>> for a 40 m asteroid and <<a90>> for a 90 m asteroid (95th percentile <<b40>> and <<b90>>) (Fig. S1a), and the largest diameter that is deflected is <<d1>> m at 1.4 GW and <<d2>> m at 30 GW with a 10 m aperture (Fig. S1b). The result depends on the assumed coupling and lead time and is a limitation of the concept, not a prediction.",
               a40=sci(float(np.interp(math.log(40), np.log(D_ast), q50_))), a90=sci(float(np.interp(math.log(90), np.log(D_ast), q50_))), b40=sci(float(np.interp(math.log(40), np.log(D_ast), q95_))), b90=sci(float(np.interp(math.log(90), np.log(D_ast), q95_))),
               d1="less than 1" if float(np.interp(math.log(1.4), np.log(Pg_), lp_["10"])) < 1 else n(float(np.interp(math.log(1.4), np.log(Pg_), lp_["10"])), 0), d2=n(lp_["10"][-1], 0))))
adds(("fig", "FigS1_asteroid.png", "Fig. S1. (a) Achieved over required displacement against asteroid diameter for 1.4 GW and a 10 m aperture (median and 5–95% band; shaded: 40–90 m class). (b) Largest diameter that is deflected against the emitted power for three apertures.", 6.2))

adds(("h1", "S6. Reproducibility"))
adds(("p", fmt("The repository (%s, version %s) contains the model (lantp_core.py, lantp_mission.py), the studies (lantp_studies.py), the figure code (lantp_figures.py), the results (results/results.json), the automated tests (tests/test_all.py) and the manuscript sources. "
               "Commands: python lantp_studies.py --all runs every study (about 40 min on one core) and writes results/results.json and the figures; python tests/test_all.py runs the tests. Every study uses fixed seeds (base seed %s; the Monte Carlo draws use seed %s). "
               "Dependencies: Python 3, numpy, scipy, matplotlib; Cantera for the validation of the thermodynamics. The design inputs are the ranges of Table @T:rng@ (listed with their nominal values in results/results.json under params)." % (GITHUB, VERSION, R["seed"], MC["seed"]))))
