# -*- coding: utf-8 -*-
"""
lantp_core.py -- model of a laser-assisted nuclear thermal propulsion (LANTP) tug for Earth-Moon logistics.

Hydrogen thermodynamics (statistical thermodynamics of H2 <-> 2H), frozen / partially recombined / shifting-equilibrium nozzle expansion, reactor + laser enthalpy balance,
Gaussian-beam capture with pointing jitter, finite-burn departure and braking burns in a planar two-body model with Earth/Moon occultation and link dropouts,
a mass model of the tug (engine, receiver, tanks, payload, round trip), the laser-node infrastructure (electrical storage, waste-heat buffer, optics) and the comparison with a
conventional (reactor-only) nuclear thermal tug carrying the same payload on the same trajectory.

Units: SI unless stated; orbital mechanics in km and s.  ALL DESIGN-LEVEL INPUTS ARE ASSUMED RANGES, NOT MEASUREMENTS.
"""
import math
from dataclasses import dataclass

import numpy as np

G0 = 9.80665
RU = 8.314462618
NA = 6.02214076e23
KB = 1.380649e-23
HP = 6.62607015e-34
M_H2 = 2.01588e-3            # kg/mol
M_H = 1.00794e-3
TH_V = 6332.0                # H2 vibrational temperature (K)
TH_R = 87.55                 # H2 rotational temperature (K)
D0 = 4.4781 * 96485.33       # J per mol H2 (dissociation energy from v = 0)
MU_E, RE = 398600.4418, 6378.137
MU_M, RM = 4902.8, 1737.4
R_MOON, V_MOON = 384400.0, 1.0222
LAMBDA = 1.07e-6


# ================================================================================================ hydrogen thermodynamics
def lnKp(T):
    """ln of the equilibrium constant Kp (Pa) of H2 <-> 2H from molecular partition functions."""
    T = np.asarray(T, float)
    mH, mH2 = M_H / NA, M_H2 / NA
    c = lambda m: 2 * math.pi * m * KB * T / HP ** 2
    qrot = T / (2 * TH_R)
    qvib = 1 / (1 - np.exp(-TH_V / T))
    return (np.log(KB * T) + 2 * math.log(2.0) + 3 * np.log(c(mH)) - 1.5 * np.log(c(mH2)) - np.log(qrot) - np.log(qvib) - D0 / (RU * T))


def alpha_eq(T, p):
    """H2 dissociation degree at equilibrium (T in K, p in Pa)."""
    K = np.exp(lnKp(T))
    return np.sqrt(K / (K + 4 * np.asarray(p, float)))


def h_h2(T):
    """molar enthalpy of H2 relative to the v=0 ground state (J/mol)"""
    T = np.asarray(T, float)
    return 3.5 * RU * T + RU * TH_V / np.expm1(TH_V / T)


def h_mix(T, a):
    """enthalpy per kg of hydrogen (J/kg) at temperature T with dissociation degree a (zero: H2 ground state at 0 K)"""
    return ((1 - a) * h_h2(T) + a * (5.0 * RU * T + D0)) / M_H2


def s_mix(T, a, p):
    """absolute entropy per mole of H2-equivalent (J/mol/K) of the H2/H mixture at T (K) and total pressure p (Pa)"""
    T = np.asarray(T, float); a = np.clip(np.asarray(a, float), 1e-12, 1 - 1e-12)
    mH, mH2 = M_H / NA, M_H2 / NA
    ntot = 1 + a
    yH2, yH = (1 - a) / ntot, 2 * a / ntot
    x = TH_V / T
    s_vib = RU * (x / np.expm1(x) - np.log1p(-np.exp(-x)))
    sH2 = RU * (1.5 * np.log(2 * math.pi * mH2 * KB * T / HP ** 2) + np.log(KB * T / (yH2 * p)) + np.log(T / (2 * TH_R)) + 3.5) + s_vib
    sH = RU * (1.5 * np.log(2 * math.pi * mH * KB * T / HP ** 2) + np.log(KB * T / (yH * p)) + math.log(2.0) + 2.5)
    return (1 - a) * sH2 + 2 * a * sH


def solve_monotone(f, target, lo, hi, shape, n=60):
    """vectorized bisection for an increasing function f(x) = target"""
    lo = np.full(shape, lo, float); hi = np.full(shape, hi, float)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        up = f(mid) < target
        lo = np.where(up, mid, lo); hi = np.where(up, hi, mid)
    return 0.5 * (lo + hi)


def temp_from_enthalpy(hc, p):
    """chamber temperature (K) of equilibrium hydrogen with specific enthalpy hc (J/kg) at pressure p (Pa)"""
    hc = np.asarray(hc, float); p = np.broadcast_to(np.asarray(p, float), hc.shape)
    return solve_monotone(lambda T: h_mix(T, alpha_eq(T, p)), hc, 50.0, 14000.0, hc.shape)


def exhaust(Tc, p_c, p_e_ratio=1e-3, phi=0.0, eta_n=0.94, mode="partial"):
    """effective exhaust velocity (m/s) for an expansion of equilibrium hydrogen from (Tc, p_c) to p_e = p_c * p_e_ratio.
    mode 'partial': composition frozen at the chamber value, a fraction phi of the dissociation energy recovered (recombination) -- phi = 0: frozen flow;
    mode 'shifting': local chemical equilibrium throughout the expansion (upper bound)."""
    Tc = np.asarray(Tc, float); p_c = np.broadcast_to(np.asarray(p_c, float), Tc.shape); phi = np.broadcast_to(np.asarray(phi, float), Tc.shape)
    a_c = alpha_eq(Tc, p_c); pe = p_c * p_e_ratio
    hc = h_mix(Tc, a_c)
    if mode == "shifting":
        s_c = s_mix(Tc, a_c, p_c)
        Te = solve_monotone(lambda T: s_mix(T, alpha_eq(T, pe), pe), s_c, 20.0, Tc, Tc.shape)
        he = h_mix(Te, alpha_eq(Te, pe))
        return eta_n * np.sqrt(2 * np.maximum(hc - he, 0.0))
    sf = lambda T: s_mix(T, a_c, pe)               # frozen composition (mole fractions of the chamber)
    # frozen composition: entropy at fixed mole fractions and exit pressure; compare with the chamber entropy at the same composition
    s_c = s_mix(Tc, a_c, p_c)
    Te = solve_monotone(sf, s_c, 20.0, Tc, Tc.shape)
    he = h_mix(Te, a_c)
    return eta_n * np.sqrt(2 * np.maximum(hc - he + phi * a_c * D0 / M_H2, 0.0))


def eq1_isp(Tc, gamma=1.4, M=M_H2, p_e_ratio=1e-3):
    """ideal-gas formula (no dissociation): Isp = (1/g0) sqrt(2 gamma/(gamma-1) R Tc/M (1-(pe/pc)^((gamma-1)/gamma)))"""
    return np.sqrt(2 * gamma / (gamma - 1) * RU * np.asarray(Tc, float) / M * (1 - p_e_ratio ** ((gamma - 1) / gamma))) / G0


# ================================================================================================ beam link
def capture(R_km, Dt, r_R, M2, jitter_urad, lam=LAMBDA, w0_frac=0.45):
    """fraction of the emitted beam captured by a circular receiver of radius r_R (m) at range R (km).  The transmitter (aperture Dt, beam waist w0 = w0_frac * Dt, beam quality M2)
    is assumed to refocus on the receiver at every range (an optimistic assumption): spot radius w = M2 lambda R / (pi w0); pointing jitter (rms per axis, microrad) is added to the spot
    size in quadrature, w_eff^2 = w^2 + 4 (jitter R)^2; captured fraction 1 - exp(-2 r_R^2 / w_eff^2) for a Gaussian profile."""
    R = np.asarray(R_km, float) * 1e3
    w0 = w0_frac * np.asarray(Dt, float)
    w2 = (np.asarray(M2, float) * lam * R / (math.pi * w0)) ** 2 + 4 * (np.asarray(jitter_urad, float) * 1e-6 * R) ** 2
    return 1 - np.exp(-2 * np.asarray(r_R, float) ** 2 / np.maximum(w2, 1e-12))


# ================================================================================================ transfer geometry (patched conics, coplanar)
def transfer_dv(tof_days):
    """impulsive TLI and LOI delta-v (km/s) for a lunar transfer of the given time of flight from a 400 km circular orbit to a 100 km circular lunar orbit;
    also returns the energy of the transfer orbit, the perigee speed and the arrival speed relative to the Moon."""
    from scipy.optimize import brentq
    rp = RE + 400.0; vc = math.sqrt(MU_E / rp); tof = tof_days * 86400.0

    def tof_of(vp):
        a = 1 / (2 / rp - vp ** 2 / MU_E); e = rp * vp ** 2 / MU_E - 1
        r = R_MOON
        if a > 0:
            cE = (1 - r / a) / e; E = math.acos(max(-1, min(1, cE)))
            return math.sqrt(a ** 3 / MU_E) * (E - e * math.sin(E))
        aa = -a; cF = (1 + r / aa) / e; F = math.acosh(cF)
        return math.sqrt(aa ** 3 / MU_E) * (e * math.sinh(F) - F)
    v_hohmann = math.sqrt(MU_E * (2 / rp - 2 / (rp + R_MOON)))
    vp = brentq(lambda v: tof_of(v) - tof, v_hohmann * (1 + 1e-10), 11.4)
    h = rp * vp; v2 = vp ** 2 - 2 * MU_E / rp + 2 * MU_E / R_MOON
    vt = h / R_MOON; vr = math.sqrt(max(v2 - vt ** 2, 0.0))
    vinf = math.hypot(vr, vt - V_MOON)
    rc = RM + 100.0
    loi = math.sqrt(vinf ** 2 + 2 * MU_M / rc) - math.sqrt(MU_M / rc)
    return dict(dv_tli=vp - vc, dv_loi=loi, eps_tli=vp ** 2 / 2 - MU_E / rp, vp=vp, vinf=vinf, vp_circ=vc)


# ================================================================================================ propulsion table (specific impulse against received laser power)
@dataclass
class Design:
    """vectors (one entry per sample) of the design and uncertain parameters"""
    P_R: np.ndarray            # reactor thermal power (W)
    T_core: np.ndarray         # core outlet temperature limit (K)
    p_c: np.ndarray            # chamber pressure (Pa)
    phi: np.ndarray            # nozzle recombination fraction
    eta_n: np.ndarray          # nozzle efficiency
    rho: np.ndarray            # design useful laser power / reactor power
    T_in: float = 100.0
    p_e_ratio: float = 1e-3


def make_table(D, K=160, mode="partial"):
    """specific impulse (s) at K+1 equally spaced fractions of the design laser power; returns table (N, K+1), mdot (kg/s), T_c table"""
    N = D.P_R.shape[0]
    h_core = h_mix(D.T_core, alpha_eq(D.T_core, D.p_c)); h_in = h_mix(np.full(N, D.T_in), alpha_eq(np.full(N, D.T_in), D.p_c))
    mdot = D.P_R / (h_core - h_in)
    fr = np.linspace(0, 1, K + 1)[None, :]
    rho_k = D.rho[:, None] * fr
    hc = h_core[:, None] + rho_k * (h_core - h_in)[:, None]
    p = D.p_c[:, None] * np.ones_like(hc)
    Tc = temp_from_enthalpy(hc, p)
    ve = exhaust(Tc, p, D.p_e_ratio, D.phi[:, None] * np.ones_like(hc), D.eta_n[:, None] * np.ones_like(hc), mode)
    return ve / G0, mdot, Tc, h_core, h_in


def rho_for_Tc(Tc_target, T_core, p_c, T_in=100.0):
    N = np.shape(T_core)[0]
    h_core = h_mix(T_core, alpha_eq(T_core, p_c)); h_in = h_mix(np.full(N, T_in), alpha_eq(np.full(N, T_in), p_c))
    hc = h_mix(np.full(N, Tc_target), alpha_eq(np.full(N, Tc_target), p_c))
    return (hc - h_core) / (h_core - h_in)


def lookup(table, frac):
    """linear interpolation of the Isp table at laser fraction frac (0..1) for every sample"""
    K = table.shape[1] - 1
    x = np.clip(frac, 0, 1) * K
    i = np.minimum(x.astype(int), K - 1); w = x - i
    r = np.arange(table.shape[0])
    return table[r, i] * (1 - w) + table[r, i + 1] * w


# ================================================================================================ finite burns
@dataclass
class Link:
    Dt: np.ndarray
    r_R: np.ndarray
    M2: np.ndarray
    jit: np.ndarray            # microrad
    drop_rate: np.ndarray      # dropouts per hour
    t_reacq: np.ndarray        # s
    t_out: np.ndarray = None   # time (s) at which the laser is lost for good (contingency study); None: never


def _node_occulted(rs, rn, Rbody):
    """line of sight between ship (rs) and node (rn) blocked by the body of radius Rbody (km): minimum distance of the segment from the centre"""
    d = rn - rs
    t = np.clip(-np.sum(rs * d, axis=-1) / np.maximum(np.sum(d * d, axis=-1), 1e-9), 0, 1)
    cp = rs + t[..., None] * d
    return np.linalg.norm(cp, axis=-1) < Rbody


def burn(kind, mu, rc, eps_target, table, mdot, rho_frac, link, m0, laser_on, Rbody, margin, node_km=1000.0, t_half=0.0, vp=None, dt=10.0, tmax=30000.0, rng=None, rec=False):
    """finite burn, planar two-body motion.
    kind 'depart': start on the circular orbit radius rc, prograde thrust until the specific orbital energy reaches eps_target (km^2/s^2).
    kind 'brake' : start t_half seconds before periapsis (radius rc, speed vp) of the approach orbit, retrograde thrust until the energy falls to that of the circular orbit.
    table: Isp table over fractions of the design laser power; rho_frac scales the laser power actually received at full capture (1: design power).
    returns propellant burned (kg), burn time (s), and optionally time histories"""
    N = m0.shape[0]
    rng = rng or np.random.default_rng(1)
    n_node = math.sqrt(mu / rc ** 3)
    th_node0 = node_km / rc
    if kind == "depart":
        r = np.stack([np.full(N, rc), np.zeros(N)], 1); v = np.stack([np.zeros(N), np.full(N, math.sqrt(mu / rc))], 1)
        node_phase = lambda t: th_node0 + n_node * t
        sign = 1.0
    else:
        # periapsis state on the +x axis, velocity +y; propagate backward for t_half
        r = np.stack([np.full(N, rc), np.zeros(N)], 1); v = np.stack([np.zeros(N), np.full(N, vp)], 1)
        nb = max(int(t_half / 2.0), 1)
        for _ in range(nb):
            r, v = _rk4(r, v, -2.0, mu)
        th_ship = np.arctan2(r[:, 1], r[:, 0])
        # node on the circular orbit; at periapsis time it is node_km ahead
        node_phase = lambda t: (node_km / rc) + n_node * (t - t_half) + 0.0
        sign = -1.0
    m = m0.copy(); t = 0.0
    done = np.zeros(N, bool); burned = np.zeros(N); tb = np.zeros(N)
    drop_left = np.zeros(N)
    rng_u = rng.random
    hist = []
    eps_circ = -mu / (2 * rc)
    p_drop = link.drop_rate / 3600.0 * dt
    while t < tmax and not done.all():
        act = ~done
        th = node_phase(t) if kind == "depart" else node_phase(t) + 0.0
        if kind == "depart":
            rn = np.stack([rc * np.cos(th) * np.ones(N), rc * np.sin(th) * np.ones(N)], 1)
        else:
            rn = np.stack([rc * np.cos(th) * np.ones(N), rc * np.sin(th) * np.ones(N)], 1)
        Rk = np.linalg.norm(rn - r, axis=1)
        occ = _node_occulted(r, rn, Rbody + margin)
        cap = capture(Rk, link.Dt, link.r_R, link.M2, link.jit)
        newdrop = rng_u(N) < p_drop
        drop_left = np.where(newdrop & (drop_left <= 0), link.t_reacq, drop_left)
        up = (drop_left <= 0) & (~occ) & laser_on
        if link.t_out is not None:
            up &= t < link.t_out
        frac = np.where(up, cap * rho_frac, 0.0)
        isp = lookup(table, frac)
        ve = isp * G0
        F = mdot * ve                       # N
        sp = np.linalg.norm(v, axis=1)
        acc = sign * F / m / 1000.0         # km/s^2 along the velocity
        dm = mdot * dt
        # integrate one step (RK4 with constant thrust acceleration direction along the velocity)
        r2, v2 = _rk4_thrust(r, v, dt, mu, acc)
        eps = 0.5 * np.sum(v2 * v2, 1) - mu / np.linalg.norm(r2, axis=1)
        fin = (eps >= eps_target) if kind == "depart" else (eps <= eps_circ + 1e-3 * abs(eps_circ))
        take = act
        r = np.where(take[:, None], r2, r); v = np.where(take[:, None], v2, v)
        m = np.where(take, m - dm, m); burned = np.where(take, burned + dm, burned); tb = np.where(take, tb + dt, tb)
        bad = (m < 500.0) & act
        burned = np.where(bad, 1e12, burned)
        done |= (fin | bad) & act
        drop_left = np.maximum(drop_left - dt, 0)
        t += dt
        if rec:
            hist.append((t, Rk.copy(), occ.copy(), isp.copy(), cap.copy()))
    return burned, tb, hist


def _acc_grav(r, mu):
    d = np.linalg.norm(r, axis=1)[:, None]
    return -mu * r / d ** 3


def _rk4(r, v, dt, mu):
    k1v = _acc_grav(r, mu); k1r = v
    k2v = _acc_grav(r + 0.5 * dt * k1r, mu); k2r = v + 0.5 * dt * k1v
    k3v = _acc_grav(r + 0.5 * dt * k2r, mu); k3r = v + 0.5 * dt * k2v
    k4v = _acc_grav(r + dt * k3r, mu); k4r = v + dt * k3v
    return r + dt / 6 * (k1r + 2 * k2r + 2 * k3r + k4r), v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)


def _rk4_thrust(r, v, dt, mu, acc):
    """RK4 step with thrust acceleration acc (km/s^2, signed) along the instantaneous velocity direction"""
    def f(rr, vv):
        sp = np.linalg.norm(vv, axis=1)[:, None]
        return vv, _acc_grav(rr, mu) + acc[:, None] * vv / np.maximum(sp, 1e-9)
    k1r, k1v = f(r, v)
    k2r, k2v = f(r + 0.5 * dt * k1r, v + 0.5 * dt * k1v)
    k3r, k3v = f(r + 0.5 * dt * k2r, v + 0.5 * dt * k2v)
    k4r, k4v = f(r + dt * k3r, v + dt * k3v)
    return r + dt / 6 * (k1r + 2 * k2r + 2 * k3r + k4r), v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
