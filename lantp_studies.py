# -*- coding: utf-8 -*-
"""
lantp_studies.py -- studies, results and figures of the LANTP cislunar power-closure assessment.

    python lantp_studies.py --all      full run (about 20-40 min), writes results/results.json and figures/*.png
    python lantp_studies.py --quick    small run for the tests
    python lantp_studies.py --figures  redraw the figures from results/results.json

ALL DESIGN-LEVEL INPUTS (efficiencies, specific masses, link parameters, coupling coefficients) ARE ASSUMED RANGES, NOT MEASUREMENTS.
"""
import argparse
import json
import math
import os
import time
from dataclasses import replace

import numpy as np
from scipy import stats

import lantp_core as L
import lantp_mission as Mi

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results"); FIG = os.path.join(HERE, "figures")
SEED = 2027
G0 = L.G0
CLAIMS = dict(isp=(1300.0, 1500.0), thrust_kN=(50.0, 120.0), laser_MW=(1.0, 50.0), reactor_MWt=(100.0, 500.0), imleo_reduction=0.40, Tc=4500.0)


def q(a, p=(5, 50, 95)):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    return [float(np.percentile(a, x)) for x in p] if a.size else [None] * len(p)


def isp_nominal(Tc, p_c=3e6, phi=0.3, eta=0.94, mode="partial"):
    Tc = np.atleast_1d(np.asarray(Tc, float))
    return L.exhaust(Tc, np.full(Tc.shape, p_c), Mi.P_E_RATIO, phi, eta, mode) / G0


# ================================================================================================ 1. thermochemistry and validation
def study_thermo():
    T = np.linspace(2000, 7000, 101)
    out = {"T": T.tolist()}
    for p in (2e6, 3e6, 7e6):
        out["alpha_%d" % (p / 1e6)] = L.alpha_eq(T, np.full(T.shape, p)).tolist()
    out["frozen"] = isp_nominal(T, 3e6, 0.0).tolist(); out["partial"] = isp_nominal(T, 3e6, 0.3).tolist(); out["shifting"] = isp_nominal(T, 3e6, 0.0, 0.94, "shifting").tolist()
    out["eq1_14"] = L.eq1_isp(T, 1.4, p_e_ratio=Mi.P_E_RATIO).tolist(); out["eq1_13"] = L.eq1_isp(T, 1.3, p_e_ratio=Mi.P_E_RATIO).tolist()
    # validation against Cantera (NASA-7 data, equilibrium and isentropic expansion) and against an independent Gibbs-minimisation of the two-species mixture
    val = {"alpha": [], "isp": []}
    try:
        import cantera as ct
        g = ct.Solution("h2o2.yaml")
        for Tt, P in ((2800, 3e6), (3000, 1e5), (3500, 3e6), (4000, 1e5), (4500, 3e6), (5500, 3e6), (6000, 3e6)):
            g.TPX = Tt, P, "H2:1"; g.equilibrate("TP"); xh = g["H"].X[0]; a_ct = xh / (xh + 2 * g["H2"].X[0])
            val["alpha"].append(dict(T=Tt, p=P, mine=float(L.alpha_eq(Tt, P)), ref=float(a_ct)))
        for Tc, pc in ((3500., 3e6), (4500., 3e6), (5500., 3e6), (4500., 7e6)):
            pe = pc * Mi.P_E_RATIO
            g.TPX = Tc, pc, "H2:1"; g.equilibrate("TP"); hc = g.enthalpy_mass; s = g.entropy_mass; X = g.X
            g.SPX = s, pe, X; fr = math.sqrt(2 * (hc - g.enthalpy_mass)) / G0
            g.TPX = Tc, pc, "H2:1"; g.equilibrate("TP"); g.SP = s, pe; g.equilibrate("SP"); sh = math.sqrt(2 * (hc - g.enthalpy_mass)) / G0
            mf = float(L.exhaust(np.array([Tc]), np.array([pc]), Mi.P_E_RATIO, 0.0, 1.0, "partial")[0] / G0)
            ms = float(L.exhaust(np.array([Tc]), np.array([pc]), Mi.P_E_RATIO, 0.0, 1.0, "shifting")[0] / G0)
            val["isp"].append(dict(Tc=Tc, p_c=pc, frozen_mine=mf, frozen_ref=fr, shifting_mine=ms, shifting_ref=sh, frozen_mine94=0.94 * mf, shifting_mine94=0.94 * ms, frozen_ref94=0.94 * fr, shifting_ref94=0.94 * sh))
        val["tool"] = "Cantera " + ct.__version__ + " (h2o2.yaml)"
    except Exception as e:      # pragma: no cover
        val["error"] = str(e)
    # independent numerical Gibbs minimisation (scipy) of the two-species mixture at fixed T, p, using the same standard Gibbs energies
    from scipy.optimize import minimize_scalar
    gib = []
    for Tt, P in ((3000, 1e5), (4500, 3e6), (6000, 3e6)):
        K = float(np.exp(L.lnKp(Tt)))
        G_ = lambda a: (1 - a) * (0.0 + L.RU * Tt * math.log((1 - a) / (1 + a) * P / 1e5)) + 2 * a * (0.5 * -L.RU * Tt * math.log(K / 1e5) + L.RU * Tt * math.log(2 * a / (1 + a) * P / 1e5))
        r = minimize_scalar(G_, bounds=(1e-9, 1 - 1e-9), method="bounded", options=dict(xatol=1e-12))
        gib.append(dict(T=Tt, p=P, gibbs=float(r.x), analytic=float(L.alpha_eq(Tt, P))))
    val["gibbs"] = gib
    out["validation"] = val
    # materials: the chamber temperature of the claimed performance against the highest reported melting / sublimation temperatures of refractory solids (assumed handbook values)
    out["materials_K"] = {"tungsten": 3695, "graphite (sublimation, 1 atm)": 3900, "tantalum carbide": 4150, "hafnium carbide": 4200, "tantalum hafnium carbide (reported maximum)": 4260, "core limit used": 2800}
    return out


# ================================================================================================ 2. power closure
def study_power(n=1500, seed=SEED):
    S = Mi.sample(n, seed)
    rho = np.geomspace(0.01, 6.0, 40)
    res = []
    for r in rho:
        D = Mi.make_design(S, rho=r)
        tab, mdot, Tc, hc, hi = L.make_table(D, K=4)
        res.append(tab[:, -1])
    res = np.array(res)                                 # (rho, n)
    S0 = Mi.nominal(1)
    fro = []; shf = []
    for r in rho:
        D = Mi.make_design(S0, rho=r); h = L.h_mix(D.T_core, L.alpha_eq(D.T_core, D.p_c)); hi_ = L.h_mix(np.array([100.]), L.alpha_eq(np.array([100.]), D.p_c))
        Tc = L.temp_from_enthalpy(h + r * (h - hi_), D.p_c)
        fro.append(float(L.exhaust(Tc, D.p_c, Mi.P_E_RATIO, 0.0, 0.94, "partial")[0] / G0)); shf.append(float(L.exhaust(Tc, D.p_c, Mi.P_E_RATIO, 0.0, 0.94, "shifting")[0] / G0))
    out = dict(rho=rho.tolist(), q05=np.percentile(res, 5, axis=1).tolist(), q50=np.percentile(res, 50, axis=1).tolist(), q95=np.percentile(res, 95, axis=1).tolist(), frozen=fro, shifting=shf)
    # claimed 1-50 MW laser on a 100-500 MWt reactor
    out["rho_claim"] = [CLAIMS["laser_MW"][0] / CLAIMS["reactor_MWt"][1], CLAIMS["laser_MW"][1] / CLAIMS["reactor_MWt"][0]]
    cl = np.array([1.0 / 500.0, 50.0 / 100.0])
    Dn = Mi.make_design(Mi.nominal(2), rho=cl)
    tab, *_ = L.make_table(Dn, K=4)
    out["isp_at_claimed_laser"] = (tab[:, -1]).tolist()
    # Isp NTP only
    out["isp_ntp"] = q(res[0])
    # power needed for the claimed Isp (median parameters): rho at Isp 1300 / 1400 / 1500
    need = {}
    for target in (1300.0, 1400.0, 1500.0):
        rr = np.geomspace(0.01, 8.0, 400); Dg = Mi.make_design(Mi.nominal(len(rr)), rho=rr); tab, *_ = L.make_table(Dg, K=1)
        i = int(np.argmax(tab[:, -1] >= target)); need[str(int(target))] = float(rr[i]) if tab[:, -1].max() >= target else None
    out["rho_needed"] = need
    return out


def study_laser_thrust(n=1200, seed=SEED + 1):
    S = Mi.sample(n, seed)
    F = np.linspace(20e3, 150e3, 14)
    out = {"F_kN": (F / 1e3).tolist()}
    for target in (1300.0, 1400.0, 1500.0):
        rr = np.geomspace(0.02, 30.0, 220)
        # per sample: find rho giving the target Isp (monotone table), then the chain of powers
        D = Mi.make_design(S, rho=np.full(n, 30.0)); tab, mdot, Tc, hcore, hin = L.make_table(D, K=300)
        fr = np.linspace(0, 1, 301)[None, :]
        i = np.argmax(tab >= target, axis=1); ok = tab.max(axis=1) >= target
        rho_t = np.where(ok, D.rho * fr[0, i], np.nan)
        ve = target * G0
        rows = []
        for f in F:
            md = f / ve
            P_R = md * (hcore - hin)
            P_use = rho_t * P_R
            P_emit = P_use / (S["eta_coup"] * S["eta_abs"] * Mi.FIXED["eta_opt"] * L.capture(Mi.FIXED["node_km"], Mi.FIXED["Dt"], Mi.FIXED["r_R"], S["M2"], S["jit"]))
            rows.append(dict(P_R=q(P_R / 1e6), P_use=q(P_use / 1e6), P_emit=q(P_emit / 1e6)))
        out[str(int(target))] = rows
    return out


# ================================================================================================ 3. beam link
def study_beam():
    R = np.geomspace(1e2, 1e6, 200)
    out = {"R_km": R.tolist()}
    for key, (Dt, jit) in {"D5": (5.0, 0.05), "D10": (10.0, 0.05), "D20": (20.0, 0.05), "D10_j": (10.0, 0.3)}.items():
        out[key] = L.capture(R, Dt, 3.0, 1.2, jit).tolist()
    # range at which the captured fraction falls to 0.5 and 0.1 against the aperture and jitter
    tab = []
    for Dt in (5.0, 10.0, 20.0, 40.0, 100.0):
        for jit in (0.02, 0.05, 0.1, 0.3):
            Rr = np.geomspace(1e2, 3e6, 4000); c = L.capture(Rr, Dt, 3.0, 1.2, jit)
            r50 = float(Rr[np.argmax(c < 0.5)]) if (c < 0.5).any() else None; r10 = float(Rr[np.argmax(c < 0.1)]) if (c < 0.1).any() else None
            tab.append(dict(Dt=Dt, jit=jit, r50=r50, r10=r10))
    out["range_table"] = tab
    out["segments_km"] = dict(LEO_L1=3.2e5, L1_LLO=6.0e4, TLI_limit=4.0e4, LOI_limit=2.0e3)
    out["capture_at_segments"] = {k: float(L.capture(v, 10.0, 3.0, 1.2, 0.05)) for k, v in dict(LEO_L1=3.2e5, L1_LLO=6.0e4, TLI_end=2.9e4, LOI_start=1e3).items()}
    # captured fraction with a 3 m receiver for the largest apertures, and the aperture / receiver radius needed for a captured fraction of 0.5 (jitter 0.05 microrad, M2 = 1.2)
    best = {}
    for name, Rk in (("LOI_start", 1e3), ("TLI_end", 2.9e4), ("L1_LLO", 6e4), ("LEO_L1", 3.2e5)):
        Dg = np.geomspace(0.5, 3000, 3000); c = L.capture(Rk, Dg, 3.0, 1.2, 0.05)
        rr = np.geomspace(0.1, 3000, 3000); cr = L.capture(Rk, 10.0, rr, 1.2, 0.05)
        best[name] = dict(R_km=Rk, capture_10m=float(L.capture(Rk, 10.0, 3.0, 1.2, 0.05)), capture_100m=float(L.capture(Rk, 100.0, 3.0, 1.2, 0.05)), capture_max=float(c.max()),
                          Dt_for_half=float(Dg[np.argmax(c >= 0.5)]) if (c >= 0.5).any() else None, r_R_for_half_10m=float(rr[np.argmax(cr >= 0.5)]) if (cr >= 0.5).any() else None)
    out["best"] = best
    return out


# ================================================================================================ 4. mission studies
def design_arrays(S, rho=None):
    return Mi.make_design(S, rho=rho)


def run_pair(S, rho=None, fixed=None, laser=(1, 1), receiver=True, link=None, mode="partial", record=False):
    D = Mi.make_design(S, rho=rho); D0 = Mi.make_design(S, rho=0.0)
    fx = dict(legs=2); fx.update(fixed or {})
    r = Mi.solve_mission(S, D, receiver=receiver, laser=laser, mode=mode, fixed=fx, link=link, record=record)
    n = Mi.solve_mission(S, D0, receiver=False, mode=mode, fixed=fx, link=None)
    return r, n, D


def mc_main(n=1500, seed=SEED + 2):
    S = Mi.sample(n, seed)
    r, nt, D = run_pair(S)
    ratio = r["M"] / nt["M"]
    inf = Mi.infrastructure(S, D, r, fixed=dict(legs=2))
    # effective specific impulse over the burns: impulsive delta-v over g * ln(mass ratio) of the TLI burn (finite burn included)
    mTLI0 = r["M"]; mTLI1 = r["M"] - r["c"][0]
    out = dict(n=n, seed=seed, S={k: v.tolist() for k, v in S.items()}, rho=D.rho.tolist(), Tc_design=r["Tc"].tolist(), isp_design=(r["ve"] / G0).tolist(), isp_ntp=(nt["ve"] / G0).tolist(),
               M_lantp=r["M"].tolist(), M_ntp=nt["M"].tolist(), ratio=ratio.tolist(), t_tli=r["t"][0].tolist(), t_ntp_tli=nt["t"][0].tolist(), F=r["F"].tolist(), F_ntp=nt["F"].tolist(),
               m_rec=r["m_rec"].tolist(), m_eng=r["m_eng"].tolist(), P_use=r["P_use"].tolist(),
               isp_eff_tli=(geo_dv("tli") * 1e3 / (G0 * np.log(mTLI0 / mTLI1))).tolist(),
               P_emit=inf["P_emit"].tolist(), P_elec=inf["P_elec"].tolist(), M_inf=inf["M_inf"].tolist(), M_inf_per_mission=inf["M_inf_per_mission"].tolist(), N_life=float(inf["N_life"]),
               ratio_inf=((r["M"] + inf["M_inf_per_mission"]) / nt["M"]).tolist())
    return out


def geo_dv(which):
    g = L.transfer_dv(Mi.FIXED["tof"]); return g["dv_" + which]


def study_ratio_vs_rho(n=300, seed=SEED + 3):
    out = {"rho": [0.05, 0.1, 0.25, 0.5, 1.0, 2.0], "rows": []}
    for rho in out["rho"]:
        S = Mi.sample(n, seed)
        r, nt, D = run_pair(S, rho=rho)
        ratio = r["M"] / nt["M"]
        out["rows"].append(dict(rho=rho, q=q(ratio), feasible=float(np.isfinite(ratio).mean()), Isp_med=float(np.median(r["ve"] / G0))))
    return out


def study_ratio_vs_mu(n=300, seed=SEED + 4):
    mus = [10.0, 15.0, 25.0, 40.0, 60.0, 80.0]
    out = {"mu": mus, "design": [], "rho025": []}
    for mu in mus:
        S = Mi.sample(n, seed); S["mu_rec"] = np.full(n, mu)
        r, nt, D = run_pair(S)
        out["design"].append(dict(q=q(r["M"] / nt["M"], (25, 50, 75)), feasible=float(np.isfinite(r["M"]).mean())))
        r, nt, D = run_pair(S, rho=0.25)
        out["rho025"].append(dict(q=q(r["M"] / nt["M"], (25, 50, 75)), feasible=float(np.isfinite(r["M"]).mean())))
    return out


def study_breakeven():
    """nominal tug on grids: ratio of IMLEO (and infrastructure-inclusive) against receiver specific mass, laser fraction rho, mission frequency and transfer time"""
    out = {}
    mus = np.array([2.0, 4.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0]); rhos = np.array([0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 2.4])
    MU, RH = np.meshgrid(mus, rhos, indexing="ij")
    n = MU.size
    S = Mi.nominal(n); S["mu_rec"] = MU.ravel()
    r, nt, D = run_pair(S, rho=RH.ravel())
    out["mu"] = mus.tolist(); out["rho"] = rhos.tolist(); out["ratio_mu_rho"] = (r["M"] / nt["M"]).reshape(MU.shape).tolist()
    inf = Mi.infrastructure(S, D, r, fixed=dict(legs=2))
    out["inf_over_ntp"] = (inf["M_inf"] / nt["M"]).reshape(MU.shape).tolist()
    out["spacecraft_saving_t"] = ((nt["M"] - r["M"]) / 1e3).reshape(MU.shape).tolist()
    # mission count to amortize the infrastructure: N* with (M_inf / N) = NTP - LANTP
    sav = nt["M"] - r["M"]
    Nstar = np.where(sav > 0, inf["M_inf"] / sav, np.inf)
    out["N_star"] = Nstar.reshape(MU.shape).tolist()
    # transfer time
    tofs = [1.8, 2.0, 2.5, 3.0, 4.0, 4.5]
    rows = []
    for tof in tofs:
        S1 = Mi.nominal(1); S1["mu_rec"] = np.array([10.0])
        r1, n1, _ = run_pair(S1, fixed=dict(tof=tof))
        rows.append(dict(tof=tof, ratio=float(r1["M"][0] / n1["M"][0]), dv=L.transfer_dv(tof)["dv_tli"] + L.transfer_dv(tof)["dv_loi"], t_tli=float(r1["t"][0][0])))
    out["tof"] = rows
    # payload and mission frequency
    pls = [5e3, 10e3, 20e3, 40e3, 80e3]
    out["payload"] = []
    for pl in pls:
        S1 = Mi.nominal(1); S1["mu_rec"] = np.array([10.0])
        r1, n1, _ = run_pair(S1, fixed=dict(m_pl=pl))
        out["payload"].append(dict(m_pl=pl, ratio=float(r1["M"][0] / n1["M"][0]), M_ntp=float(n1["M"][0]), M_lantp=float(r1["M"][0])))
    return out


def study_nominal(record=True):
    """nominal-design tug: powers, masses, burn timelines (Fig. 6), power chain"""
    S = Mi.nominal(1)
    D = Mi.make_design(S); D0 = Mi.make_design(S, rho=0.0)
    r = Mi.solve_mission(S, D, fixed=dict(legs=2), record=record)
    nt = Mi.solve_mission(S, D0, receiver=False, fixed=dict(legs=2))
    inf = Mi.infrastructure(S, D, r, fixed=dict(legs=2))
    out = dict(rho=float(D.rho[0]), Tc=float(r["Tc"][0]), isp=float(r["ve"][0] / G0), isp_ntp=float(nt["ve"][0] / G0), F_kN=float(r["F"][0] / 1e3), F_ntp_kN=float(nt["F"][0] / 1e3), mdot=float(r["mdot"][0]),
               M=float(r["M"][0]), M_ntp=float(nt["M"][0]), m_rec=float(r["m_rec"][0]), m_eng=float(r["m_eng"][0]), burned=float(r["burned"][0]), burned_ntp=float(nt["burned"][0]),
               t_burn=[float(x[0]) for x in r["t"][:2]], t_burn_ntp=[float(x[0]) for x in nt["t"][:2]],
               P_R=float(S["P_R"][0]), P_use=float(r["P_use"][0]), P_abs=float(inf["P_abs"][0]), P_rec=float(inf["P_rec"][0]), P_emit=float(inf["P_emit"][0]), P_elec=float(inf["P_elec"][0]),
               P_waste_node=float(inf["P_elec"][0] - inf["P_emit"][0]), P_waste_rec=float(inf["P_abs"][0] - inf["P_use"][0]),
               M_inf=float(inf["M_inf"][0]), M_inf_per_mission=float(inf["M_inf_per_mission"][0]), N_life=float(inf["N_life"]),
               infra={k: {kk: float(vv[0]) for kk, vv in inf[k].items()} for k in ("leo", "llo")}, ratio=float(r["M"][0] / nt["M"][0]), P_rec_over_use=float(inf["P_rec"][0] / r["P_use"][0]),
               geo=dict(dv_tli=geo_dv("tli"), dv_loi=geo_dv("loi")))
    if record:
        h1, h2 = r["hist"][0], r["hist"][1]
        out["tli"] = dict(t=[x[0] / 60 for x in h1], R=[float(x[1][0]) for x in h1], occ=[bool(x[2][0]) for x in h1], isp=[float(x[3][0]) for x in h1])
        out["loi"] = dict(t=[x[0] / 60 for x in h2], R=[float(x[1][0]) for x in h2], occ=[bool(x[2][0]) for x in h2], isp=[float(x[3][0]) for x in h2])
    return out


# ================================================================================================ 5. sensitivity and convergence
SENS_NAMES = {"mu_rec": "receiver specific mass", "P_R": "reactor power", "phi": "nozzle recombination $\\phi$", "p_c": "chamber pressure", "jit": "pointing jitter", "f_tank": "tank fraction",
              "t_reacq": "reacquisition time", "TW": "engine T/W", "M2": "beam quality $M^2$", "drop": "dropout rate"}


def study_sensitivity(mc):
    ratio = np.array(mc["ratio"]); ok = np.isfinite(ratio)
    rows = []
    for k, nm in SENS_NAMES.items():
        x = np.array(mc["S"][k])[ok]
        rows.append(dict(name=nm, key=k, rho=float(stats.spearmanr(x, ratio[ok]).statistic)))
    return rows


def study_convergence(mc):
    ratio = np.array(mc["ratio"]); ratio = ratio[np.isfinite(ratio)]
    Ns = np.unique(np.round(np.geomspace(20, len(ratio), 25)).astype(int))
    rng = np.random.default_rng(3); med = []
    for N in Ns:
        med.append(float(np.median(ratio[:N])))
    # bootstrap interval of the median at full N
    bs = [float(np.median(rng.choice(ratio, len(ratio)))) for _ in range(2000)]
    tof = np.linspace(1.6, 4.5, 30); dv = [L.transfer_dv(t) for t in tof]
    return dict(N=Ns.tolist(), median=med, median_ci=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], tof=tof.tolist(), dv_tli=[d["dv_tli"] for d in dv], dv_loi=[d["dv_loi"] for d in dv])


# ================================================================================================ 6. contingency
def study_contingency(n=500, seed=SEED + 5):
    S = Mi.sample(n, seed)
    D = Mi.make_design(S); D0 = Mi.make_design(S, rho=0.0)
    fx = dict(legs=2)
    nt = Mi.solve_mission(S, D0, receiver=False, fixed=fx)
    pol = {"nominal (laser on both burns)": (1, 1), "laser lost before TLI, reactor-only TLI (single fault)": (0, 1), "reactor-only mission with the LANTP hardware (full fallback)": (0, 0)}
    out = {"n": n, "policies": {}}
    for name, lf in pol.items():
        r = Mi.solve_mission(S, D, laser=(lf[0], lf[1], 0, 0), fixed=fx)
        out["policies"][name] = dict(q=q(r["M"] / nt["M"], (5, 25, 50, 75, 95)), feasible=float(np.isfinite(r["M"]).mean()), M_med=float(np.nanmedian(r["M"])))
    # outage time during TLI at nominal: propellant to complete the burn after a laser loss at time t_out (fixed vehicle mass of the nominal solution)
    S1 = Mi.nominal(1); D1 = Mi.make_design(S1)
    r1 = Mi.solve_mission(S1, D1, fixed=fx)
    tab, mdot, _, _, _ = L.make_table(D1); geo = L.transfer_dv(Mi.FIXED["tof"]); link0 = Mi._link(S1)
    rows = []
    t_nom = float(r1["t"][0][0])
    for tout in np.linspace(0, 1.2, 9) * t_nom:
        lk = replace(link0, t_out=np.array([tout]))
        c, t, h = L.burn("depart", L.MU_E, L.RE + 400.0, geo["eps_tli"], tab, mdot, np.ones(1), lk, r1["M"].copy(), np.array([True]), L.RE, 100.0, Mi.FIXED["node_km"], dt=10.0, tmax=30000.0)
        rows.append(dict(t_out_frac=float(tout / t_nom), burned_t=float(c[0] / 1e3), t_burn_min=float(t[0] / 60)))
    out["outage_curve"] = rows
    out["tli_nominal_burned_t"] = float(r1["c"][0][0] / 1e3)
    return out



def study_roundtrip():
    """round trip with propulsive return (four burns: TLI, LOI, trans-Earth injection from the lunar node, capture at the Earth node); the tug is reused. nominal vehicle, receiver specific mass 10 and 25 kg/MW"""
    rows = []
    for pl in (10e3, 20e3, 40e3):
        S = Mi.nominal(2); S["mu_rec"] = np.array([10.0, 25.0])
        D = Mi.make_design(S); D0 = Mi.make_design(S, rho=0.0)
        r = Mi.solve_mission(S, D, fixed=dict(legs=4, m_pl=pl)); nt = Mi.solve_mission(S, D0, receiver=False, fixed=dict(legs=4, m_pl=pl))
        for i, mu in enumerate((10.0, 25.0)):
            rows.append(dict(m_pl=pl, mu=mu, M_lantp=None if not np.isfinite(r["M"][i]) else float(r["M"][i]), M_ntp=None if not np.isfinite(nt["M"][i]) else float(nt["M"][i]),
                             ratio=None if not (np.isfinite(r["M"][i]) and np.isfinite(nt["M"][i])) else float(r["M"][i] / nt["M"][i])))
    return dict(rows=rows)


def study_ntp_reactor():
    """fairness of the baseline: conventional NTP with a larger reactor for payloads above the nominal one-way delivery (nominal parameters otherwise); returns initial masses (kg)"""
    out = {"P_R": [250e6, 500e6, 750e6, 1000e6, 1500e6, 2000e6], "rows": []}
    for pl in (20e3, 40e3, 80e3):
        S = Mi.nominal(len(out["P_R"])); S["P_R"] = np.array(out["P_R"])
        D0 = Mi.make_design(S, rho=0.0)
        nt = Mi.solve_mission(S, D0, receiver=False, fixed=dict(legs=2, m_pl=pl))
        S1 = Mi.nominal(1); S1["mu_rec"] = np.array([10.0]); D1 = Mi.make_design(S1)
        r1 = Mi.solve_mission(S1, D1, fixed=dict(legs=2, m_pl=pl))
        out["rows"].append(dict(m_pl=pl, M_ntp=[None if not np.isfinite(x) else float(x) for x in nt["M"]], M_lantp_10=float(r1["M"][0])))
    return out

# ================================================================================================ 7. asteroid deflection extension (illustrative)
def study_asteroid(n=800, seed=SEED + 6):
    rng = np.random.default_rng(seed)
    out = {}
    D = np.geomspace(2, 90, 18)
    for tag, P_gw, Dt in (("main", 1.4, 10.0),):
        res = []
        for d in D:
            lead = 10 ** rng.uniform(math.log10(1), math.log10(10), n) * 86400.0
            R = 10 ** rng.uniform(4.5, 5.5, n) * 1e3                       # range from the laser node to the asteroid, m
            jit = 10 ** rng.uniform(math.log10(0.05), math.log10(0.3), n)
            M2 = rng.uniform(1.1, 1.6, n)
            Cmax = 10 ** rng.uniform(math.log10(30), math.log10(300), n) * 1e-6      # N/W, plasma-regime coupling
            Ihalf = 10 ** rng.uniform(8, 10, n)                                     # W/m^2 at which half of the maximum coupling is reached
            P = P_gw * 1e9 * 0.9
            w = np.sqrt((M2 * L.LAMBDA * R / (math.pi * 0.45 * Dt)) ** 2 + 4 * (jit * 1e-6 * R) ** 2)
            area = np.minimum(math.pi * w ** 2, math.pi * (d / 2) ** 2)
            frac = np.minimum(1.0, (d / 2) ** 2 / w ** 2)
            P_on = P * frac; I = P_on / area
            Cm = Cmax * I / (I + Ihalf)
            F = Cm * P_on
            m_ast = 2500.0 * math.pi * d ** 3 / 6
            t_irr = lead * 0.5
            dv = F * t_irr / m_ast; dx = dv * lead
            res.append(dx / 6.371e6)
        res = np.array(res)
        out[tag] = dict(D=D.tolist(), q05=np.percentile(res, 5, axis=1).tolist(), q50=np.percentile(res, 50, axis=1).tolist(), q95=np.percentile(res, 95, axis=1).tolist())
    # largest deflectable diameter (achieved >= required) against emitted power and aperture, median over the uncertainty
    Ps = np.geomspace(0.3, 30, 9); ap = {}
    for Dt in (10.0, 30.0, 100.0):
        big = []
        for P_gw in Ps:
            Dgrid = np.geomspace(0.5, 200, 60); ok = []
            for d in Dgrid:
                lead = 10 ** rng.uniform(0, 1, 200) * 86400.0; R = 10 ** rng.uniform(4.5, 5.5, 200) * 1e3; jit = 10 ** rng.uniform(math.log10(0.05), math.log10(0.3), 200); M2 = rng.uniform(1.1, 1.6, 200)
                Cmax = 10 ** rng.uniform(math.log10(30), math.log10(300), 200) * 1e-6; Ihalf = 10 ** rng.uniform(8, 10, 200)
                w = np.sqrt((M2 * L.LAMBDA * R / (math.pi * 0.45 * Dt)) ** 2 + 4 * (jit * 1e-6 * R) ** 2)
                area = np.minimum(math.pi * w ** 2, math.pi * (d / 2) ** 2); frac = np.minimum(1.0, (d / 2) ** 2 / w ** 2); P_on = P_gw * 1e9 * 0.9 * frac; I = P_on / area
                F = Cmax * I / (I + Ihalf) * P_on; m_ast = 2500.0 * math.pi * d ** 3 / 6; dx = F * lead * 0.5 / m_ast * lead / 6.371e6
                ok.append(np.median(dx) >= 1.0)
            ok = np.array(ok); big.append(float(Dgrid[ok].max()) if ok.any() else 0.0)
        ap[str(int(Dt))] = big
    out["P_gw"] = Ps.tolist(); out["largest_diameter"] = ap
    return out


# ================================================================================================ 8. version 1.1.0 studies
GRID_P = (25e6, 50e6, 100e6, 250e6, 500e6, 750e6, 1000e6, 1500e6, 2000e6)


def study_opt_mc(n=500, seed=SEED + 9, eng_exp=1.0):
    """primary benchmark: the conventional tug and the laser-assisted tug each with the reactor power that minimizes their own initial mass (grid of GRID_P), same payload, trajectory and margins;
    also the laser-assisted tug at the reactor power of the draw (100-500 MWt) against the best conventional tug"""
    S = Mi.sample(n, seed)
    Ml, Mn = [], []
    for P in GRID_P:
        S2 = dict(S); S2["P_R"] = np.full(n, P)
        D = Mi.make_design(S2); D0 = Mi.make_design(S2, rho=0.0)
        r = Mi.solve_mission(S2, D, fixed=dict(legs=2, eng_exp=eng_exp)); nt = Mi.solve_mission(S2, D0, receiver=False, fixed=dict(legs=2, eng_exp=eng_exp))
        Ml.append(r["M"]); Mn.append(nt["M"])
    Ml = np.array(Ml); Mn = np.array(Mn)
    bestL = np.nanmin(np.where(np.isfinite(Ml), Ml, np.inf), axis=0); bestN = np.nanmin(np.where(np.isfinite(Mn), Mn, np.inf), axis=0)
    iL = np.argmin(np.where(np.isfinite(Ml), Ml, np.inf), axis=0); iN = np.argmin(np.where(np.isfinite(Mn), Mn, np.inf), axis=0)
    ratio_opt = bestL / bestN
    # laser-assisted tug at the reactor power of the draw, against the best conventional tug
    S3 = Mi.sample(n, seed)
    D = Mi.make_design(S3); r = Mi.solve_mission(S3, D, fixed=dict(legs=2, eng_exp=eng_exp))
    ratio_claim_reactor = r["M"] / bestN
    return dict(n=n, grid_MW=[p / 1e6 for p in GRID_P], ratio_opt=ratio_opt.tolist(), ratio_claim_reactor=ratio_claim_reactor.tolist(), best_P_lantp=[GRID_P[i] / 1e6 for i in iL], best_P_ntp=[GRID_P[i] / 1e6 for i in iN],
                M_lantp_opt=bestL.tolist(), M_ntp_opt=bestN.tolist(), q_ratio_opt=q(ratio_opt, (5, 25, 50, 75, 95)), q_ratio_claim_reactor=q(ratio_claim_reactor, (5, 25, 50, 75, 95)),
                share_below_1=float(np.mean(ratio_opt < 1)), share_below_06=float(np.mean(ratio_opt <= 0.6)))


def study_opt_scaling(n=150, seed=SEED + 21):
    """audit of the reactor-size scaling of the optimized benchmark: the engine-system mass (reactor, shield, nozzle) is proportional to thrust at the nominal T/W (exponent 1); here it scales as
    P_R**x relative to its value at 500 MWt for x = 0.7 (larger reactors lighter per unit thrust), 1.0 and 1.3 (larger reactors heavier per unit thrust)"""
    rows = []
    for x in (0.7, 1.0, 1.3):
        r = study_opt_mc(n=n, seed=seed, eng_exp=x)
        rows.append(dict(exp=x, q_ratio_opt=r["q_ratio_opt"], share_below_1=r["share_below_1"], P_ntp_median=float(np.median(r["best_P_ntp"])), P_lantp_median=float(np.median(r["best_P_lantp"])),
                         P_ntp_q=q(r["best_P_ntp"], (5, 50, 95)), P_lantp_q=q(r["best_P_lantp"], (5, 50, 95)), M_ntp_median=float(np.median(r["M_ntp_opt"])), M_lantp_median=float(np.median(r["M_lantp_opt"]))))
    return dict(n=n, rows=rows)


SOBOL_KEYS = ["mu_rec", "P_R", "T_core", "p_c", "phi", "eta_n", "jit", "M2", "drop", "t_reacq", "f_tank", "TW", "eta_coup", "eta_abs"]
SOBOL_NAMES = {"mu_rec": "receiver specific mass", "P_R": "reactor power", "T_core": "core temperature limit", "p_c": "chamber pressure", "phi": "nozzle recombination", "eta_n": "nozzle efficiency", "jit": "pointing jitter",
               "M2": "beam quality", "drop": "dropout rate", "t_reacq": "reacquisition time", "f_tank": "tank fraction", "TW": "engine T/W", "eta_coup": "coupling efficiency", "eta_abs": "absorption efficiency"}


def _map_unit(U, keys):
    S = {k: np.full(U.shape[0], v, float) for k, v in Mi.NOMINAL.items()}
    for j, k in enumerate(keys):
        lo, hi, d = Mi.RANGES[k]
        S[k] = lo + (hi - lo) * U[:, j] if d == "u" else lo * (hi / lo) ** U[:, j]
    return S


def _sobol_indices(f, N):
    """Saltelli (2010) first-order and Jansen total-order estimators from the matrix of model outputs f (rows: A, B, AB_1..AB_k)"""
    fA, fB = f[0][:N], f[1][:N]; k = f.shape[0] - 2
    var = np.var(np.concatenate([fA, fB]), ddof=1)
    S1 = np.array([np.mean(fB * (f[2 + i][:N] - fA)) / var for i in range(k)])
    ST = np.array([0.5 * np.mean((fA - f[2 + i][:N]) ** 2) / var for i in range(k)])
    return S1, ST


def study_sobol(N=2048, seed=SEED + 10, nboot=300, chunk=4096):
    """variance-based sensitivity of the IMLEO ratio. Scrambled Sobol quasi-random sequence (2k dimensions: A = first k, B = last k columns), Saltelli (2010) first-order and Jansen total-order
    estimators, bootstrap intervals for both, convergence with the sample size N (the first N rows of a Sobol sequence are again a Sobol sequence), and the same indices for the logarithm of the ratio"""
    from scipy.stats import qmc
    k = len(SOBOL_KEYS)
    X = qmc.Sobol(d=2 * k, scramble=True, seed=seed).random(N)
    A, B = X[:, :k], X[:, k:]
    mats = [A, B] + [np.where(np.arange(k)[None, :] == i, B, A) for i in range(k)]
    U = np.vstack(mats); out = []
    for lo in range(0, U.shape[0], chunk):
        r, nt, D = run_pair(_map_unit(U[lo:lo + chunk], SOBOL_KEYS)); out.append(r["M"] / nt["M"])
    f = np.concatenate(out).reshape(len(mats), N)
    rng = np.random.default_rng(seed)
    res = {}
    for tag, g in (("ratio", f), ("log", np.log(f))):
        S1, ST = _sobol_indices(g, N); b1, bt = [], []
        for _ in range(nboot):
            ix = rng.integers(0, N, N); gg = g[:, ix]; s1, st = _sobol_indices(gg, N); b1.append(s1); bt.append(st)
        b1, bt = np.array(b1), np.array(bt)
        conv = {}
        for n in [m for m in (128, 256, 512, 1024, 2048, 4096) if m <= N]:
            s1, st = _sobol_indices(g, n); conv[str(n)] = dict(S1=s1.tolist(), ST=st.tolist())
        res[tag] = dict(S1=S1.tolist(), ST=ST.tolist(), S1_lo=np.percentile(b1, 2.5, axis=0).tolist(), S1_hi=np.percentile(b1, 97.5, axis=0).tolist(),
                        ST_lo=np.percentile(bt, 2.5, axis=0).tolist(), ST_hi=np.percentile(bt, 97.5, axis=0).tolist(), convergence=conv, var=float(np.var(g[:2].ravel(), ddof=1)))
    d = dict(N=N, keys=SOBOL_KEYS, names=[SOBOL_NAMES[x] for x in SOBOL_KEYS], evaluations=int(U.shape[0]), sampling="scrambled Sobol sequence", **res["ratio"])
    d["log"] = res["log"]
    return d


def study_threshold(nrho=12, nmu=14):
    """technology-threshold map of the nominal vehicle: IMLEO ratio on a fine grid of useful laser power and receiver specific mass, the receiver specific mass at which the ratio is 1, 0.9 and 0.6,
    and the chamber temperature of each laser power"""
    P_R = Mi.NOMINAL["P_R"]
    rho = np.geomspace(0.1, 2.4, nrho); mu = np.geomspace(1.0, 60.0, nmu)
    RH, MU = np.meshgrid(rho, mu, indexing="ij")
    S = Mi.nominal(RH.size); S["mu_rec"] = MU.ravel()
    r, nt, D = run_pair(S, rho=RH.ravel())
    Z = (r["M"] / nt["M"]).reshape(RH.shape)
    out = dict(rho=rho.tolist(), mu=mu.tolist(), P_use_GW=(rho * P_R / 1e9).tolist(), ratio=Z.tolist())
    Tc = []
    for rr in rho:
        S1 = Mi.nominal(1); D1 = Mi.make_design(S1, rho=rr); h = L.h_mix(D1.T_core, L.alpha_eq(D1.T_core, D1.p_c)); hi_ = L.h_mix(np.array([100.0]), L.alpha_eq(np.array([100.0]), D1.p_c))
        Tc.append(float(L.temp_from_enthalpy(h + rr * (h - hi_), D1.p_c)[0]))
    out["Tc"] = Tc
    for level in (1.0, 0.9, 0.6):
        out["mu_star_%g" % level] = []
        for i in range(nrho):
            ys = Z[i, :]; xs = mu
            m = None
            for j in range(len(xs) - 1):
                if (ys[j] - level) * (ys[j + 1] - level) <= 0 and ys[j] != ys[j + 1]:
                    m = float(math.exp(math.log(xs[j]) + (level - ys[j]) / (ys[j + 1] - ys[j]) * (math.log(xs[j + 1]) - math.log(xs[j])))); break
            if m is None and ys[0] < level:
                m = float(xs[-1])          # ratio stays below the level over the whole range
            out["mu_star_%g" % level].append(m)
    return out


def study_node_offset():
    """sensitivity to the phasing of the laser nodes: initial separation between node and vehicle at the start of each burn (km); nominal vehicle"""
    rows = []
    for off in (500.0, 1000.0, 3000.0, 10000.0, 20000.0, 30000.0):
        S = Mi.nominal(1); D = Mi.make_design(S); D0 = Mi.make_design(S, rho=0.0)
        r = Mi.solve_mission(S, D, fixed=dict(legs=2, node_km=off), record=True); nt = Mi.solve_mission(S, D0, receiver=False, fixed=dict(legs=2))
        h = r["hist"][0]
        rows.append(dict(offset_km=off, ratio=float(r["M"][0] / nt["M"][0]), M=float(r["M"][0]), t_tli_min=float(r["t"][0][0] / 60), t_loi_min=float(r["t"][1][0] / 60),
                         R_max_km=float(max(x[1][0] for x in h)), occulted_min=float(sum(1 for x in h if x[2][0]) * 10 / 60), isp_min=float(min(x[3][0] for x in h))))
    return dict(rows=rows)


def study_independent_burn():
    """independent integration of finite burns with an adaptive 8th-order Runge-Kutta scheme (scipy DOP853, tight tolerances, event at the target energy) against the fixed-step
    vectorized integrator of the mission model, constant specific impulse (laser off); TLI and the lunar departure burn"""
    from scipy.integrate import solve_ivp
    S = Mi.nominal(1); D0 = Mi.make_design(S, rho=0.0)
    tab, mdot, *_ = L.make_table(D0); ve = float(tab[0, -1]) * G0; md = float(mdot[0]); geo = L.transfer_dv(2.0); link = Mi._link(S)
    rows = []
    for name, mu, rc, eps, dt in (("TLI", L.MU_E, L.RE + 400.0, geo["eps_tli"], 10.0), ("lunar departure", L.MU_M, L.RM + 100.0, geo["vinf"] ** 2 / 2, 4.0)):
        for M in (40e3, 80e3, 160e3):
            def f(t, y):
                x, yy, vx, vy, m = y; r = math.hypot(x, yy); v = math.hypot(vx, vy); a = md * ve / m / 1000.0
                return [vx, vy, -mu * x / r ** 3 + a * vx / v, -mu * yy / r ** 3 + a * vy / v, -md]
            ev = lambda t, y: 0.5 * (y[2] ** 2 + y[3] ** 2) - mu / math.hypot(y[0], y[1]) - eps
            ev.terminal = True; ev.direction = 1
            sol = solve_ivp(f, [0, 40000], [rc, 0.0, 0.0, math.sqrt(mu / rc), M], method="DOP853", rtol=1e-11, atol=1e-9, events=ev)
            m_ind = M - sol.y[4, -1]; t_ind = float(sol.t[-1])
            c, t, _ = L.burn("depart", mu, rc, eps, tab, mdot, np.ones(1), link, np.array([M]), np.array([False]), L.RE if mu == L.MU_E else L.RM, 100.0, 1000.0, dt=dt, tmax=40000.0)
            rows.append(dict(burn=name, M=M, propellant_independent=float(m_ind), propellant_model=float(c[0]), diff=float(c[0] / m_ind - 1), t_independent=t_ind, t_model=float(t[0])))
    # limiting case: a near-impulsive burn (thrust 40 times the nominal) of the mission model against the rocket equation with the impulsive delta-v of the same transfer (physical check of the mass flow and of the delta-v bookkeeping)
    lim = []
    for name, mu, rc, eps, dv, dt in (("TLI", L.MU_E, L.RE + 400.0, geo["eps_tli"], geo["dv_tli"], 0.1), ("lunar departure", L.MU_M, L.RM + 100.0, geo["vinf"] ** 2 / 2, math.sqrt(geo["vinf"] ** 2 + 2 * L.MU_M / (L.RM + 100.0)) - math.sqrt(L.MU_M / (L.RM + 100.0)), 0.05)):
        for M in (40e3, 80e3, 160e3):
            c, t, _ = L.burn("depart", mu, rc, eps, tab, mdot * 40, np.ones(1), link, np.array([M]), np.array([False]), L.RE if mu == L.MU_E else L.RM, 100.0, 1000.0, dt=dt, tmax=3000.0)
            ref = M * (1 - math.exp(-dv * 1e3 / ve))
            lim.append(dict(burn=name, M=M, dv=float(dv), propellant_model=float(c[0]), propellant_rocket_equation=float(ref), diff=float(c[0] / ref - 1)))
    return dict(rows=rows, limit=lim)



# ================================================================================================ driver
def run_all(quick=False):
    os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
    k = 0.15 if quick else 1.0
    t0 = time.time(); R = dict(seed=SEED, claims=CLAIMS, params=dict(ranges={a: list(b[:2]) + [b[2]] for a, b in Mi.RANGES.items()}, nominal=Mi.NOMINAL, fixed=Mi.FIXED, p_e_ratio=Mi.P_E_RATIO))

    def step(name, fn, *a, **kw):
        R[name] = fn(*a, **kw); print(name, round(time.time() - t0, 1), flush=True)
    step("thermo", study_thermo)
    step("power", study_power, max(int(1500 * k), 200))
    step("laser_thrust", study_laser_thrust, max(int(1200 * k), 200))
    step("beam", study_beam)
    step("nominal", study_nominal)
    step("mc", mc_main, max(int(1500 * k), 60))
    step("sensitivity", study_sensitivity, R["mc"])
    step("convergence", study_convergence, R["mc"])
    step("ratio_rho", study_ratio_vs_rho, max(int(300 * k), 40))
    step("ratio_mu", study_ratio_vs_mu, max(int(300 * k), 40))
    step("breakeven", study_breakeven)
    step("contingency", study_contingency, max(int(500 * k), 50))
    step("roundtrip", study_roundtrip)
    step("ntp_reactor", study_ntp_reactor)
    step("asteroid", study_asteroid, max(int(800 * k), 100))
    step("opt_mc", study_opt_mc, max(int(500 * k), 40))
    step("sobol", study_sobol, 256 if not quick else 24)
    step("threshold", study_threshold)
    step("node_offset", study_node_offset)
    step("independent_burn", study_independent_burn)
    R["runtime_s"] = round(time.time() - t0, 1)
    path = os.path.join(RES, "results_quick.json" if quick else "results.json")
    json.dump(R, open(path, "w"), indent=1, default=float)
    if not quick:
        import lantp_figures
        lantp_figures.make_all(R)
    return R


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--all", action="store_true"); ap.add_argument("--quick", action="store_true"); ap.add_argument("--figures", action="store_true")
    a = ap.parse_args()
    if a.figures:
        import lantp_figures
        lantp_figures.make_all(json.load(open(os.path.join(RES, "results.json"))))
    else:
        R = run_all(quick=a.quick); print("done", R["runtime_s"], "s")
