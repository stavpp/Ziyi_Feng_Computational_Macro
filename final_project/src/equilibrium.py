"""The stationary equilibrium: one wrapper for Huggett (1993) and Aiyagari (1994), as in week 8.

An economy is a borrowing limit (in its grids), a wage function w(r), and a demand function D(r). The
distribution block `aggregate` turns (r, w) into asset supply A(r), and `stationary_equilibrium` bisects on
the excess supply A(r) - D(r), passing the solution of one step to the next as a warm start.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np

from src.aggregation import mean_assets, stationary_dist, transition_matrix
from src.household import solve_household
from src.model import Grids, make_grids


@dataclass
class Aggregates:
    A: float  # mean assets A(r), the households' asset supply
    lam: np.ndarray  # the stationary distribution, N_a x N_z
    C: np.ndarray  # consumption policy
    G: np.ndarray  # savings policy


@dataclass
class Economy:
    name: str
    gri: Grids  # the grids, with the borrowing limit of this economy
    wage: Callable  # w(r)
    demand: Callable  # D(r): what absorbs the households' assets at the rate r


def aggregate(r, w, par, mpar, gri, warm=None):
    """The distribution block at prices (r, w): household -> policy chain -> stationary distribution -> A(r).

    warm: the Aggregates of a nearby r, used as the starting point, or None for a cold start.
    """
    C, G, _ = solve_household(r, w, par, mpar, gri, C0=None if warm is None else warm.C)
    Q = transition_matrix(G, gri)
    lam, _ = stationary_dist(Q, mpar, gri, lam0=None if warm is None else warm.lam)
    return Aggregates(A=mean_assets(lam, gri), lam=lam, C=C, G=G)


def stationary_equilibrium(eco, par, mpar, lo, hi):
    """Bisection on the excess supply A(r) - D(r), which increases in r. Returns r*, aggregates, steps."""
    warm, k = None, 0
    while hi - lo > mpar.crit_r:
        mid = (lo + hi) / 2
        warm = aggregate(mid, eco.wage(mid), par, mpar, eco.gri, warm)  # A(mid), warm start
        excess = warm.A - eco.demand(mid)
        lo, hi = (mid, hi) if excess < 0 else (lo, mid)  # negative excess supply: the root is above mid
        k += 1
    return (lo + hi) / 2, warm, k


def huggett_economy(par, mpar, amin=-2.0):
    """Huggett: a bond in zero net supply between households, wage 1, borrowing down to amin."""
    return Economy(name="Huggett", gri=make_grids(amin, par, mpar), wage=lambda r: 1.0, demand=lambda r: 0.0)


def aiyagari_economy(par, mpar):
    """Aiyagari: capital rented to a firm with Y = K^alpha L^(1 - alpha), prices from the firm.

    The borrowing limit is zero.
    """
    gri = make_grids(0.0, par, mpar)
    L = gri.lam_z @ gri.z  # aggregate labour: mean efficiency E[z]

    def K_demand(r):
        # r = alpha (K/L)^(alpha - 1) - delta, solved for K
        return L * ((r + par.delta) / par.alpha) ** (1 / (par.alpha - 1))

    def wage(r):
        # the wage that goes with capital demand at r: w = (1 - alpha) (K/L)^alpha
        return (1 - par.alpha) * (K_demand(r) / L) ** par.alpha

    return Economy(name="Aiyagari", gri=gri, wage=wage, demand=K_demand)


def output(K, par, gri):
    """Production Y = K^alpha L^(1 - alpha) with L = E[z]."""
    L = gri.lam_z @ gri.z
    return K**par.alpha * L ** (1 - par.alpha)
