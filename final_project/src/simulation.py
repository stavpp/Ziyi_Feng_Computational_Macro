"""Monte Carlo simulation of a panel of households (session 6).

The only random part of the project. The generator is created from the seed inside the function and passed
along, never the global state: the same seed gives the same panel on every machine.
"""

import numpy as np


def simulate_panel(G, gri, N, T, seed):
    """N households for T periods from the borrowing limit. Returns the final cross section of assets."""
    rng = np.random.default_rng(seed)  # one generator, made from the seed, every draw below comes from it
    cum = np.cumsum(gri.Pi, axis=1)  # cumulated rows of Pi, built once
    a = np.full(N, gri.a[0])  # everybody starts at the limit
    m = rng.choice(len(gri.z), size=N, p=gri.lam_z)  # income indices drawn from the stationary distribution
    for _ in range(T):
        anew = np.empty(N)
        for k in range(len(gri.z)):  # (i) tomorrow's assets: one interpolation per income state
            sel = m == k
            anew[sel] = np.interp(a[sel], gri.a, G[:, k])
        a = anew
        u = rng.random(N)  # (ii) tomorrow's income: one uniform per household
        m = np.minimum((u[:, None] > cum[m]).sum(axis=1), len(gri.z) - 1)  # the first n with F_mn >= u
    return a


def mean_assets_by_simulation(G, gri, N, T, seeds):
    """Mean assets of the simulated cross section over several seeds: mean, standard error, the values."""
    means = np.array([simulate_panel(G, gri, N, T, seed).mean() for seed in seeds])
    return means.mean(), means.std(ddof=1) / np.sqrt(len(means)), means
