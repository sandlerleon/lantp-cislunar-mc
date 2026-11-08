# -*- coding: utf-8 -*-
"""Manuscript, part A: Introduction, architecture and models (Sections 1-5)."""
from common import *

PRM = R["params"]
NM, RG, FX = PRM["nominal"], PRM["ranges"], PRM["fixed"]

# ============================================================================================ 1 Introduction
add(("h1", "1. Introduction"))
add(("p", "Nuclear thermal propulsion (NTP) heats hydrogen in a reactor core and expands it through a nozzle. Its specific impulse, about twice that of the best chemical engines, is limited by the temperature the core can withstand, which for the carbide fuels of the NERVA lineage is below about 3000 K "
          "[@Ludewig2006;@Qualls2011]. NTP has been studied for lunar transportation [@Reynolds2019], where its high thrust at moderate specific impulse suits short transfers. Beaming laser power to a vehicle has a long history in launch and space propulsion "
          "[@Minovitch1972;@Kare1995;@Mertogul1990], and orbital power beaming systems for cislunar space are under study [@Carrio2025]. Laser-assisted nuclear thermal propulsion (LANTP) combines the two: the reactor heats the hydrogen to the core limit and a beam from orbital laser nodes adds power in the chamber, "
          "so that a higher chamber temperature, hydrogen dissociation and a higher specific impulse become available without raising the core temperature."))
add(("p", "A concept of this kind has been described with the following claims: a specific impulse of 1300–1500 s at a chamber temperature of about 4500 K, a thrust of 50–120 kN, a laser of the \"multi-megawatt\" class (1–50 MW) on a reactor of 100–500 MWt, and a 40% lower initial mass in low Earth orbit (IMLEO) than conventional NTP for the same cislunar mission. "
          "These claims are quantitative and can be tested. Whether they hold depends on the interaction of four things that a single-discipline analysis separates: the thermodynamics of dissociating hydrogen, the power chain from the electrical supply to the propellant, the optical link between a laser node and a moving vehicle, "
          "and the mass of the receiver and of the laser infrastructure. The central question of this paper is therefore under what coupled conditions laser assistance gives a meaningful advantage over conventional NTP, and under which parameter combinations it is inferior."))
add(("p", "Three hypotheses are tested. H1: the claimed specific impulse and thrust require a laser power that is far above the claimed class. H2: the IMLEO of the laser-assisted tug exceeds that of conventional NTP over most of the assumed parameter space, because of the receiver and the finite duration of the beam link, so that the claimed 40% reduction is not reached. "
          "H3: a break-even region exists only for small receiver specific mass and low laser fraction, and it is lost when the laser infrastructure, a single laser fault or the constraint of the link are included. The paper makes four contributions: a coupled feasibility boundary of the thermochemical, optical and mass models; "
          "an infrastructure-aware comparison that amortizes the laser nodes over a number of missions; a reliability-aware evaluation with the propellant reserve for laser outages; and a set of explicit, falsifiable conditions (Section 7)."))

# ============================================================================================ 2 System architecture
add(("h1", "2. System architecture"))
add(("fig", "Fig1_architecture.png", "Fig. @F:arch@. Architecture of the laser-assisted transfer between low Earth orbit and low lunar orbit: laser nodes in low Earth orbit (Beamer 1) and low lunar orbit (retro-beamer 3), an Earth–Moon L1 relay for tracking and communication, and a bimodal tug that carries a reactor and a beam receiver (schematic, not to scale).", 6.4))
add(("p", "The vehicle is a bimodal tug: a reactor of thermal power $P_R$ heats hydrogen, stored cryogenically at about 20 K and preheated to $T_{in}$ = 100 K, to the core outlet temperature limit $T_{core}$ (assumed 2600–2900 K); a beam receiver adds a useful laser power $P_{use}=ρP_R$ to the same flow, so that the chamber enthalpy is "
          "$h_c=h_{core}+ρ(h_{core}-h_{in})$. The mass flow $\\dot m=P_R/(h_{core}-h_{in})$ is set by the reactor alone. The reactor-only case, $ρ=0$, is the conventional NTP reference. The laser nodes are a node in low Earth orbit that beams during trans-lunar injection (TLI), "
          "a node in low lunar orbit that beams (as a retro-beamer) during lunar orbit insertion (LOI), and a relay at the Earth–Moon L1 point used for tracking and data, not for power (Fig. @F:arch@). The mission delivers a payload of %s t from a 400 km circular orbit to a 100 km circular lunar orbit in a transfer of %s days; "
          "the tug is expended in the main comparison, and a round trip with a propulsive return is examined as a sensitivity (Section 6.8)." % (n(FX["m_pl"] / 1e3), n(FX["tof"], 1))))

# ============================================================================================ 3 Thermochemical model
add(("h1", "3. Thermochemical and nozzle model"))
add(("p", "Hydrogen at the chamber conditions is treated as an equilibrium mixture of H$_2$ and H with the dissociation degree $α$ given by $K_p=4α^2p/(1-α^2)$. The equilibrium constant follows from the partition functions of the two species, with a rigid rotor and harmonic oscillator for H$_2$ (rotational temperature 87.55 K, vibrational temperature 6332 K), "
          "a doublet ground state of the atom and the dissociation energy 4.4781 eV from the vibrational ground state [@Herzberg1961]. The enthalpy per kg is $h=[(1-α)h_{H_2}(T)+α(5RT+D_0)]/M_{H_2}$ and the entropy of the mixture is built from the same partition functions. "
          "The chamber temperature follows from the enthalpy balance of Section 2 at the chamber pressure $p_c$ (assumed 2–7 MPa; 3 MPa nominal)."))
add(("p", "The exhaust velocity of an expansion to $p_e=10^{-4}p_c$ with nozzle efficiency $η_n$ (0.92–0.96) is computed in three ways. In the frozen expansion the composition of the chamber is kept and the temperature follows from the isentropic condition; the dissociation energy is lost. "
          "In the partial expansion a fraction $φ$ (0–0.5) of the dissociation energy is recovered by recombination in the nozzle. In the shifting-equilibrium expansion the mixture is in chemical equilibrium throughout, which gives an upper bound. "
          "The ideal-gas formula $I_{sp}=g_0^{-1}\\{[2γ/(γ-1)](RT_c/M)[1-(p_e/p_c)^{(γ-1)/γ}]\\}^{1/2}$ with $M$ = 2.016 g/mol and γ of 1.3 or 1.4, which does not include dissociation, is shown for comparison. "
          "The implementation was validated against Cantera [@Cantera] with NASA polynomial data (equilibrium composition, and isentropic expansions with frozen and equilibrium composition; Table @T:val@) and against an independent numerical minimization of the Gibbs energy, and compared in method with the NASA chemical-equilibrium program [@McBride1994]."))

# ============================================================================================ 4 Optical and power model
add(("h1", "4. Optical and power model"))
add(("p", "Four powers are distinguished. The useful thermal power delivered to the propellant is $P_{use}=ρP_R$. The power absorbed by the receiver is $P_{abs}=P_{use}/η_{coup}$, with a coupling efficiency $η_{coup}$ (0.80–0.95) that accounts for re-radiation and conduction losses of a receiver at the chamber temperature; the difference is waste heat on the vehicle. "
          "The power received at the aperture is $P_{rec}=P_{abs}/η_{abs}$ with an absorption efficiency $η_{abs}$ (0.90–0.99). The emitted power is $P_{emit}=P_{rec}/(η_{opt}η_{cap})$ with transmitter optics efficiency $η_{opt}$ = 0.9 and the captured fraction $η_{cap}$ of the link. "
          "The electrical power drawn by the laser is $P_{elec}=P_{emit}/η_{wp}$ with a wall-plug efficiency $η_{wp}$ (0.3–0.5), and the difference is waste heat at the node."))
add(("p", "The link is a Gaussian beam. The transmitter aperture $D_t$ (10 m unless stated) gives a waist $w_0=0.45D_t$ and the beam is assumed to be refocused on the receiver at every range, an optimistic assumption, so that the spot radius is $w=M^2λR/(πw_0)$ at range $R$, with wavelength λ = 1.07 µm and beam quality $M^2$ (1.1–1.6) [@Siegman1986]. "
          "Pointing jitter $σ_θ$ (0.05–0.3 µrad rms per axis) is added to the spot size in quadrature, $w_{eff}^2=w^2+4(σ_θR)^2$, and a receiver of radius $r_R$ = 3 m captures $η_{cap}=1-\\exp(-2r_R^2/w_{eff}^2)$. "
          "The beam is lost when the line of sight between the node and the vehicle passes through the Earth (with a 100 km atmospheric margin) or the Moon (20 km margin), and Poisson dropouts (0.01–0.5 per hour), each followed by a re-acquisition time of 10–120 s, interrupt it. "
          "The captured fraction, the occultation and the dropouts are evaluated along the simulated trajectory."))

# ============================================================================================ 5 Mission and mass model
add(("h1", "5. Mission, mass and uncertainty model"))
add(("h2", "5.1 Transfer geometry and finite burns"))
add(("p", "The transfer is a coplanar patched-conic transfer from a 400 km circular orbit to a 100 km circular lunar orbit. The perigee speed is solved for the time of flight (2 days nominal, 1.6–4.5 days studied), which gives an impulsive $Δv_{TLI}$ of %s km/s and $Δv_{LOI}$ of %s km/s at 2 days [@Bate1971]. "
          "The burns are integrated as finite burns in the central body's two-body field with thrust along the velocity: TLI is a prograde burn from the circular orbit until the orbital energy of the transfer orbit is reached; LOI is a retrograde burn centered on periselene until the orbit is circular. "
          "The thrust is $F=\\dot m\\,g_0I_{sp}(t)$ with $I_{sp}$ interpolated from a table of specific impulse against the laser power received, which changes with the captured fraction, so that gravity losses, the growth of the node–vehicle range, occultation and dropouts all enter the propellant used. "
          "The laser node is on a circular orbit 1000 km ahead of the vehicle at the start of each burn." % (n(NOM["geo"]["dv_tli"], 2), n(NOM["geo"]["dv_loi"], 2))))
add(("h2", "5.2 Mass model and comparison with conventional NTP"))
add(("p", "The initial mass $M$ satisfies $M=m_{pl}+m_{fix}+(1+f_t)(1+f_r)m_{burned}(M)$, where $m_{pl}$ = %s t is the payload, $m_{fix}=m_{eng}+m_{rec}+m_{misc}$, $m_{eng}=F/(g_0\\,T/W)$ with an engine thrust-to-weight $T/W$ of 3–8, "
          "$m_{rec}=μ_{rec}P_{abs}$ with a receiver specific mass $μ_{rec}$ of 15–80 kg per MW absorbed (assumed), $m_{misc}$ = %s t of structure and avionics, $f_t$ is the tank mass fraction (0.12–0.25), and $f_r$ = %s a residual and boil-off allowance. "
          "$m_{burned}(M)$ is the propellant used by the simulated burns for the initial mass $M$, and the equation is solved for the smallest $M$ that closes. The conventional NTP reference uses the same reactor, payload, trajectory, margins and burn simulation with $ρ=0$ and no receiver. "
          "The IMLEO ratio is $M_{LANTP}/M_{NTP}$; the claimed 40%% reduction corresponds to 0.6." % (n(FX["m_pl"] / 1e3), n(FX["m_misc"] / 1e3, 1), n(FX["f_res"], 2))))
add(("h2", "5.3 Laser infrastructure"))
add(("p", "Each laser node is sized for the emitted power $P_{emit}$ at the start of the burn and the energy $E_{emit}=P_{emit}t_{on}$ of the burns it serves (TLI for the node in low Earth orbit, LOI for the node in low lunar orbit). The electrical supply is a battery buffer of mass $E_{emit}/(η_{wp}e_s)$ with specific energy $e_s$ of 150–500 Wh/kg, "
          "a waste-heat buffer of mass $E_{emit}(1/η_{wp}-1)/c_s$ with a heat capacity $c_s$ of 0.5–3 MJ/kg, the laser and its optics at 100–1000 kg per MW emitted, an aperture of 10–30 kg/m², and a solar array that recharges the buffer between missions (%s missions per year). "
          "Buffering the burn energy rather than supplying the peak power directly is the lighter choice for a duty cycle of hours per mission; the result is therefore a lower bound on the node mass. The infrastructure is amortized over %s missions (%s years). "
          "A mass of %s t is added for the relay." % (n(FX["missions_per_year"]), n(FX["missions_per_year"] * FX["life_years"]), n(FX["life_years"]), n(FX["m_relay"] / 1e3, 1))))
add(("h2", "5.4 Contingency policies"))
add(("p", "Three policies are compared for the tank loading. In the nominal policy the vehicle carries the propellant for laser-assisted burns. In the single-fault policy it carries the propellant to complete TLI on the reactor alone, so that a laser outage before TLI does not strand the vehicle. "
          "In the full-fallback policy it carries the propellant for a reactor-only mission with the LANTP hardware. The propellant to complete TLI after a loss of the laser at a time $t_{out}$ is also computed for the nominal vehicle."))
add(("h2", "5.5 Uncertainty analysis"))
add(("p", fmt("The uncertain parameters of Table @T:rng@ are sampled independently (uniform or log-uniform between the limits, assumed) with <<N>> independent random draws; the laser power fraction is that required to reach a chamber temperature of 4500 K at the sampled chamber pressure and core temperature. "
              "The distributions of the specific impulse and of the IMLEO ratio are reported with their 5th, 50th and 95th percentiles, the influence of the inputs by Spearman rank correlation with the IMLEO ratio, and the convergence by the median against the number of draws with a bootstrap interval. "
              "Break-even surfaces are computed on grids of receiver specific mass, laser power fraction, payload and transfer time for the nominal vehicle, and the infrastructure-inclusive ratio $(M_{LANTP}+M_{inf}/N)/M_{NTP}$ gives the number of missions $N^*$ at which the nodes are amortized. "
              "All inputs are assumed ranges, not measurements; the results are conditional on them.", N=n(MC["n"]))))
rows = []
LBL = {"P_R": ("Reactor thermal power", "MW", 1e-6), "T_core": ("Core outlet temperature limit", "K", 1), "p_c": ("Chamber pressure", "MPa", 1e-6), "phi": ("Nozzle recombination fraction φ", "–", 1), "eta_n": ("Nozzle efficiency", "–", 1),
       "mu_rec": ("Receiver specific mass", "kg/MW absorbed", 1), "TW": ("Engine thrust-to-weight", "–", 1), "f_tank": ("Tank mass fraction", "–", 1), "jit": ("Pointing jitter (rms per axis)", "µrad", 1), "M2": ("Beam quality M²", "–", 1),
       "drop": ("Link dropout rate", "per hour", 1), "t_reacq": ("Re-acquisition time", "s", 1), "eta_coup": ("Coupling efficiency", "–", 1), "eta_abs": ("Absorption efficiency", "–", 1), "eta_wp": ("Laser wall-plug efficiency", "–", 1),
       "e_spec": ("Energy buffer specific energy", "Wh/kg", 1), "c_s": ("Waste-heat buffer capacity", "MJ/kg", 1e-6), "a_las": ("Laser and optics specific mass", "kg/MW emitted", 1), "a_ap": ("Aperture areal density", "kg/m²", 1)}
for k, (nm, un, sc) in LBL.items():
    lo, hi, dist = RG[k]
    rows.append([nm, un, n(lo * sc, 2 if hi * sc < 20 else 0), n(hi * sc, 2 if hi * sc < 20 else 0), "log-uniform" if dist == "lu" else "uniform", n(NM[k] * sc, 2 if hi * sc < 20 else 0)])
add(("table", "Table @T:rng@. Uncertain parameters of the Monte Carlo analysis (assumed ranges) and the nominal values used for the break-even grids.", ["Parameter", "Unit", "Low", "High", "Distribution", "Nominal"], rows, [2.8, 1.5, 0.8, 0.8, 1.1, 0.9], 15))
