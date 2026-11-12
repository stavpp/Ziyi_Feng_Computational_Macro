"""run_all.py: every figure and table of the write-up, from scratch, into output/. About 15 seconds.

    python run_all.py

Writes output/figures/wealth.pdf, output/tables/equilibrium.tex, output/tables/numbers.tex and output/log.txt.
Every seed of the project is set here.
"""

import time
from pathlib import Path

import numpy as np

from src.equilibrium import aiyagari_economy, output, stationary_equilibrium
from src.figures import equilibrium_table, numbers_file, wealth_figure
from src.model import EconomicParameters, NumericalParameters
from src.simulation import mean_assets_by_simulation

OUT = Path(__file__).parent / "output"
SEEDS = range(5)  # the seeds of the Monte Carlo check: five runs, the standard error across them is reported
N_SIM, T_SIM = 10_000, 500  # households and periods per simulation


def main():
    t_start = time.perf_counter()
    par, mpar = EconomicParameters(), NumericalParameters()
    log = []

    # 1. The Aiyagari equilibrium: bisection on r between 0 and the complete markets rate 1/beta - 1
    eco = aiyagari_economy(par, mpar)
    r_cm = 1 / par.beta - 1
    r_star, agg, steps = stationary_equilibrium(eco, par, mpar, 0.0, r_cm - 1e-4)
    K_star = agg.A
    log.append(f"Aiyagari: r* = {100 * r_star:.3f} percent after {steps} bisection steps, K* = {K_star:.3f}")

    # 2. The Monte Carlo check at r*: the simulated mean against Young's, with its standard error across seeds
    A_sim, se_sim, _ = mean_assets_by_simulation(agg.G, eco.gri, N_SIM, T_SIM, SEEDS)
    log.append(f"simulation at r*: mean assets {A_sim:.3f}, s.e. over {len(SEEDS)} seeds {se_sim:.3f}")

    # 3. The figure and the tables of the write-up
    wealth_figure(agg.lam, eco.gri, OUT / "figures" / "wealth.pdf")
    K_cm = eco.demand(r_cm)
    rows = [
        ("Interest rate $r^*$ (percent)", 100 * r_star, ".2f"),
        ("Capital $K^*$", K_star, ".2f"),
        ("Capital to output $K^* / Y^*$", K_star / output(K_star, par, eco.gri), ".2f"),
        ("Wage $w^*$", eco.wage(r_star), ".3f"),
        ("Share of households at the borrowing limit", agg.lam[0].sum(), ".3f"),
        ("Capital under complete markets", K_cm, ".2f"),
        ("Simulated mean assets at $r^*$ ($N = 10{,}000$, $5$ seeds)", A_sim, ".3f"),
        ("Standard error across seeds", se_sim, ".3f"),
    ]
    equilibrium_table(rows, OUT / "tables" / "equilibrium.tex")
    numbers_file(
        [
            ("rstar", 100 * r_star, ".2f"),
            ("Kstar", K_star, ".2f"),
            ("Kcm", K_cm, ".2f"),
            ("Kgain", 100 * (K_star / K_cm - 1), ".0f"),
            ("bisectionsteps", steps, "d"),
        ],
        OUT / "tables" / "numbers.tex",
    )

    log.append(f"run_all.py finished in {time.perf_counter() - t_start:.1f} s, numpy {np.__version__}")
    (OUT / "log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
