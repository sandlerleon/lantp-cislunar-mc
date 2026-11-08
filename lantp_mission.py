# -*- coding: utf-8 -*-
"""lantp_mission.py -- sampling of the uncertain design, round-trip mission mass model, laser-node infrastructure, contingency policies.  ASSUMED RANGES ONLY."""
import math
from dataclasses import dataclass, replace

import numpy as np

import lantp_core as L

P_E_RATIO = 1e-4
TC_DESIGN = 4500.0


# ------------------------------------------------------------------------------------------------ sampling
RANGES = {   # name: (low, high, distribution)
    "P_R": (100e6, 500e6, "u"), "T_core": (2600.0, 2900.0, "u"), "p_c": (2e6, 7e6, "lu"), "phi": (0.0, 0.5, "u"), "eta_n": (0.92, 0.96, "u"),
    "mu_rec": (15.0, 80.0, "lu"), "TW": (3.0, 8.0, "u"), "f_tank": (0.12, 0.25, "u"), "jit": (0.05, 0.3, "lu"), "M2": (1.1, 1.6, "u"),
    "drop": (0.01, 0.5, "lu"), "t_reacq": (10.0, 120.0, "u"), "eta_coup": (0.8, 0.95, "u"), "eta_abs": (0.9, 0.99, "u"), "eta_wp": (0.3, 0.5, "u"),
    "e_spec": (150.0, 500.0, "lu"), "c_s": (0.5e6, 3e6, "lu"), "a_las": (100.0, 1000.0, "lu"), "a_ap": (10.0, 30.0, "u"),
}
NOMINAL = dict(P_R=500e6, T_core=2800.0, p_c=3e6, phi=0.3, eta_n=0.94, mu_rec=25.0, TW=5.0, f_tank=0.18, jit=0.05, M2=1.2, drop=0.05, t_reacq=30.0, eta_coup=0.9, eta_abs=0.95,
               eta_wp=0.4, e_spec=250.0, c_s=1.5e6, a_las=300.0, a_ap=15.0)
FIXED = dict(Dt=10.0, r_R=3.0, eta_opt=0.9, m_pl=20000.0, m_misc=3000.0, f_res=0.05, missions_per_year=6.0, life_years=15.0, tof=2.0, node_km=1000.0, m_relay=2000.0, eng_exp=1.0, P_ref=500e6)


def sample(n, seed=2027, nominal_except=None):
    """dict of arrays; nominal_except: names that are sampled while all others stay at their nominal value"""
    rng = np.random.default_rng(seed)
    out = {}
    for k, (lo, hi, d) in RANGES.items():
        if nominal_except is not None and k not in nominal_except:
            out[k] = np.full(n, NOMINAL[k]); continue
        u = rng.random(n)
        out[k] = lo + (hi - lo) * u if d == "u" else lo * (hi / lo) ** u
    return out


def nominal(n=1, **kw):
    s = {k: np.full(n, v, float) for k, v in NOMINAL.items()}
    for k, v in kw.items():
        s[k] = np.full(n, v, float)
    return s


def make_design(S, rho=None, Tc=TC_DESIGN):
    p_c = S["p_c"]
    rho_ = L.rho_for_Tc(Tc, S["T_core"], p_c) if rho is None else (np.full(S["P_R"].shape, rho) if np.isscalar(rho) else rho)
    return L.Design(S["P_R"], S["T_core"], p_c, S["phi"], S["eta_n"], rho_, p_e_ratio=P_E_RATIO)


# ------------------------------------------------------------------------------------------------ the mission
def _link(S, t_out=None):
    n = S["P_R"].shape[0]
    return L.Link(np.full(n, FIXED["Dt"]) if "Dt" not in S else S["Dt"], np.full(n, FIXED["r_R"]), S["M2"], S["jit"], S["drop"], S["t_reacq"], t_out)


def burned_chain(M, tables, mdot, rho_frac, link, geo, flags, pl=None, rng_seed=7, rec=None, legs=4, node_km=None):
    pl = FIXED["m_pl"] if pl is None else pl
    node_km = FIXED["node_km"] if node_km is None else node_km
    """propellant burned by the four burns of the round trip (TLI, LOI, TEI, LEO capture) starting from the mass M (kg); flags: laser on per burn (bool arrays)"""
    n = M.shape[0]
    m = M.copy(); b = []; times = []; tup = []
    rng = np.random.default_rng(rng_seed)
    # burn 1: TLI (Earth, departure)
    tbl = tables
    c1, t1, h1 = L.burn("depart", L.MU_E, L.RE + 400.0, geo["eps_tli"], tbl, mdot, rho_frac, link, m, flags[0], L.RE, 100.0, node_km, dt=10.0, tmax=24000.0, rng=rng, rec=bool(rec))
    m = m - c1
    t_half = float(np.median(t1)) * 0.5 * geo["dv_loi"] / geo["dv_tli"]
    c2, t2, h2 = L.burn("brake", L.MU_M, L.RM + 100.0, None, tbl, mdot, rho_frac, link, m, flags[1], L.RM, 20.0, node_km, t_half=t_half, vp=math.sqrt(geo["vinf"] ** 2 + 2 * L.MU_M / (L.RM + 100.0)), dt=4.0, tmax=9000.0, rng=rng, rec=bool(rec))
    m = m - c2 - pl
    if legs == 2:
        z = np.zeros(n); ht = []
        return [c1, c2, z, z], [t1, t2, z, z], (h1, h2, [], [])
    c3, t3, h3 = L.burn("depart", L.MU_M, L.RM + 100.0, geo["vinf"] ** 2 / 2, tbl, mdot, rho_frac, link, m, flags[2], L.RM, 20.0, node_km, dt=4.0, tmax=9000.0, rng=rng, rec=bool(rec))
    m = m - c3
    t_half4 = float(np.median(t1)) * 0.5
    c4, t4, h4 = L.burn("brake", L.MU_E, L.RE + 400.0, None, tbl, mdot, rho_frac, link, m, flags[3], L.RE, 100.0, node_km, t_half=t_half4, vp=geo["vp"], dt=10.0, tmax=24000.0, rng=rng, rec=bool(rec))
    return [c1, c2, c3, c4], [t1, t2, t3, t4], (h1, h2, h3, h4)


def solve_mission(S, D, receiver=True, laser=(1, 1, 1, 1), mode="partial", nscan=48, record=False, link=None, fixed=None, **_):
    """IMLEO (kg) of the round-trip tug carrying FIXED['m_pl'] to low lunar orbit.  receiver False: reactor-only reference (rho = 0, no receiver, no laser infrastructure)."""
    F_ = dict(FIXED, **(fixed or {}))
    n = S["P_R"].shape[0]
    geo = L.transfer_dv(F_["tof"])
    tab, mdot, Tc_tab, h_core, h_in = L.make_table(D, mode=mode)
    link = link or _link(S)
    flags = [np.full(n, bool(f) and receiver) for f in laser]
    ve_full = tab[:, -1] * L.G0
    F_thr = mdot * ve_full
    m_eng = F_thr / (L.G0 * S["TW"]) * (S["P_R"] / F_["P_ref"]) ** (F_["eng_exp"] - 1.0)     # engine system (reactor, shield, nozzle, turbopump): proportional to thrust unless eng_exp differs from 1
    P_use = D.rho * D.P_R if receiver else np.zeros(n)
    P_abs = P_use / S["eta_coup"]
    m_rec = S["mu_rec"] * P_abs / 1e6 if receiver else np.zeros(n)
    m_fixed = m_eng + m_rec + F_["m_misc"]
    pl = F_["m_pl"]
    lo = np.full(n, pl + 2 * m_fixed + 1.0); hi = np.full(n, 3.0e6)

    def G(M):
        c, t, h = burned_chain(M, tab, mdot, np.ones(n), link, geo, flags, pl, rec=False, legs=F_.get("legs", 4), node_km=F_["node_km"])
        burned = sum(c)
        return M - (pl + m_fixed + (1 + S["f_tank"]) * (1 + F_["f_res"]) * burned), c, t
    # G(M) is negative for small M (the burns exhaust the propellant), positive in a window and negative again for very large M (the burns are cut off by their time limit):
    # scan upward geometrically for the first sign change and interpolate linearly
    found = np.zeros(n, bool); Mroot = np.full(n, np.nan)
    M_prev = (pl + m_fixed) * 1.02; g_prev, _c, _t = G(M_prev)
    for _ in range(nscan):
        M_new = M_prev * 1.07
        g_new, _c, _t = G(M_new)
        new = (g_new >= 0) & (g_prev < 0) & ~found
        w = np.where(new, -g_prev / np.maximum(g_new - g_prev, 1e-9), 0.0)
        Mroot = np.where(new, M_prev + w * (M_new - M_prev), Mroot); found |= new
        M_prev, g_prev = M_new, g_new
        if found.all():
            break
    M = Mroot
    g, c, t = G(np.where(found, M, lo))
    out = dict(M=M, burned=sum(c), c=c, t=t, m_eng=m_eng, m_rec=m_rec, F=F_thr, mdot=mdot, ve=ve_full, P_use=P_use, P_abs=P_abs, tab=tab, Tc=Tc_tab[:, -1], geo=geo, resid=g)
    if record:
        out["hist"] = burned_chain(M, tab, mdot, np.ones(n), link, geo, flags, pl, rec=True, legs=F_.get("legs", 4), node_km=F_["node_km"])[2]
    return out


def infrastructure(S, D, res, fixed=None):
    """laser-node infrastructure (two nodes plus a relay): emitted power, electrical energy buffer, waste-heat buffer, laser and optics, recharge array; masses in kg"""
    F_ = dict(FIXED, **(fixed or {}))
    P_use = res["P_use"]; P_abs = res["P_abs"]
    P_rec = P_abs / S["eta_abs"]
    cap0 = L.capture(F_["node_km"], F_["Dt"], F_["r_R"], S["M2"], S["jit"])
    P_emit = P_rec / (F_["eta_opt"] * cap0)
    P_elec = P_emit / S["eta_wp"]
    t = res["t"]
    # on-time of each node: LEO node serves bursts 1 and 4, LLO node bursts 2 and 3 (the laser is on for the whole burn: conservative)
    E_leo = P_emit * (t[0] + t[3]); E_llo = P_emit * (t[1] + t[2])
    out = {}
    tot = 0
    for name, E in (("leo", E_leo), ("llo", E_llo)):
        E_el = E / S["eta_wp"]
        m_batt = E_el / (S["e_spec"] * 3600.0)
        m_heat = (E_el - E) / S["c_s"]
        m_las = S["a_las"] * P_emit / 1e6
        area = math.pi * (F_["Dt"] / 2) ** 2
        m_ap = S["a_ap"] * area * np.ones_like(P_emit)
        T_rep = 365.25 * 86400.0 / F_["missions_per_year"]
        P_arr = E_el / (0.9 * T_rep)
        m_arr = P_arr / 100.0
        out[name] = dict(E_emit=E, E_elec=E_el, m_batt=m_batt, m_heat=m_heat, m_las=m_las, m_ap=m_ap, m_arr=m_arr, m_node=m_batt + m_heat + m_las + m_ap + m_arr)
        tot = tot + out[name]["m_node"]
    M_inf = tot + F_["m_relay"]
    N_life = F_["missions_per_year"] * F_["life_years"]
    out.update(P_emit=P_emit, P_elec=P_elec, P_rec=P_rec, P_abs=P_abs, P_use=P_use, M_inf=M_inf, N_life=N_life, M_inf_per_mission=M_inf / N_life)
    return out
