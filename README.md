# Laser-assisted nuclear thermal propulsion for cislunar logistics: a Monte Carlo power-closure assessment

Leon Sandler, Independent Researcher — sandler.leon@gmail.com — ORCID 0009-0007-4584-808X

Code, data and manuscript for a coupled assessment of the claims made for laser-assisted nuclear thermal propulsion (LANTP) between low Earth orbit and low lunar orbit, prepared for **Aerospace Science and Technology** (Elsevier).
Manuscript: `manuscript/LANTP_AST_Manuscript.{docx,pdf}`, supplementary information `manuscript/LANTP_Supplementary_Information.{docx,pdf}`, cover letter `manuscript/LANTP_Cover_Letter.{docx,pdf}`.
Archived on Zenodo (all versions): paper 10.5281/zenodo.24048701, code 10.5281/zenodo.24048703 (version 1.0.0: paper 10.5281/zenodo.24048702, code 10.5281/zenodo.24048704).

**All design inputs (efficiencies, specific masses, link parameters, coupling coefficients) are assumed ranges, not measurements. The performance claims tested are those of a concept description that is not cited in the manuscript; check them against the source.**

## What the study does

1. **Hydrogen thermochemistry (`lantp_core.py`).** Equilibrium H2 <-> 2H from partition functions; enthalpy and entropy; frozen, partially recombined and shifting-equilibrium nozzle expansion; validated against Cantera and an independent Gibbs minimization.
2. **Power chain and link.** Useful, absorbed, received, emitted and electrical power; waste heat; Gaussian-beam capture with refocusing and pointing jitter; occultation by the Earth and the Moon and link dropouts along finite burns.
3. **Mission and mass (`lantp_mission.py`).** Patched-conic transfer with finite burns; initial-mass closure of the laser-assisted tug and of the conventional reactor-only tug for the same payload; laser-node infrastructure (energy buffer, waste-heat buffer, laser, optics, array); contingency policies for a laser outage.
4. **Studies (`lantp_studies.py`, `lantp_figures.py`).** Power closure, emitted power against thrust, beam link, burn timelines, Monte Carlo of the initial mass, sensitivity, convergence, break-even surfaces, amortization of the nodes, contingency, round trip, and an asteroid-deflection extension.
5. **Main findings (assumed ranges).** A useful laser power of 2.2-3.6 times the reactor power is needed for 1300-1500 s; a 1-50 MW laser on a 100-500 MWt reactor gives at most about 1000 s; 50-120 kN needs gigawatts of emitted power; median IMLEO is about 1.7 times that of conventional NTP and no draw reaches the claimed 0.6; the laser nodes outweigh the tug by orders of magnitude.

## Reproduce

```
pip install -r requirements.txt
python lantp_studies.py --all      # all studies -> results/results.json and figures/ (about 15 min)
python tests/test_all.py           # automated checks
python manuscript/src/build_manuscript.py          # manuscript and supplementary information (.docx)
python manuscript/src/build_cover_letter.py        # cover letter (.docx)
python manuscript/src/build_submission_files.py    # highlights and title page (.docx)
```

Seeds are fixed (`SEED = 2027`); every number in the manuscript is read from `results/results.json`. `figures/Fig1_architecture.png` and `figures/Graphical_abstract.png` are schematics.

## License

MIT for the code, CC-BY-4.0 for the manuscript. See `LICENSE`.
