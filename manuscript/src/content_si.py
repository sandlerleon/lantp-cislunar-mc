# -*- coding: utf-8 -*-
"""Supplementary information."""
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

adds(("h1", "S4. Reproducibility"))
adds(("p", fmt("The repository (%s, version %s) contains the model (lantp_core.py, lantp_mission.py), the studies (lantp_studies.py), the figure code (lantp_figures.py), the results (results/results.json), the automated tests (tests/test_all.py) and the manuscript sources. "
               "Commands: python lantp_studies.py --all runs every study (about 30 min on one core) and writes results/results.json and the figures; python tests/test_all.py runs the tests. Every study uses fixed seeds (base seed %s; the Monte Carlo draws use seed %s). "
               "Dependencies: Python 3, numpy, scipy, matplotlib; Cantera for the validation of the thermodynamics. The design inputs are the ranges of Table @T:rng@ (listed with their nominal values in results/results.json under params)." % (GITHUB, VERSION, R["seed"], MC["seed"]))))
