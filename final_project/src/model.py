"""The model: parameters, grids, and the income process.

Everything that defines the economy before any solution method is applied. Nothing in this file runs on
import, the launch file calls these functions. Replace the contents with your own model and keep the shape:
parameters in frozen dataclasses, grids built by one function.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EconomicParameters:
    gamma: float = 2.0  # relative risk aversion
    beta: float = 0.96  # discount factor
    rho: float = 0.9  # persistence of ln z
    sig_eps: float = 0.2  # standard deviation of the innovation to ln z
    alpha: float = 0.36  # capital share (Aiyagari)
    delta: float = 0.08  # depreciation rate (Aiyagari)


@dataclass(frozen=True)
class NumericalParameters:
    na: int = 200  # asset grid points N_a
    nz: int = 7  # income grid points N_z
    amax: float = 100.0  # upper grid bound a_{N_a}
    crit_pol: float = 1e-8  # the EGM stops when the policy moves by less
    crit_dist: float = 1e-12  # the distribution iteration stops when lam moves by less
    crit_r: float = 1e-6  # the bisection on r stops when the bracket is narrower
    maxiter: int = 100_000  # iteration cap, the safety net


@dataclass(frozen=True)
class Grids:
    a: np.ndarray  # asset grid, N_a
    z: np.ndarray  # income grid, N_z
    Pi: np.ndarray  # transition matrix, N_z x N_z
    lam_z: np.ndarray  # stationary distribution of the income chain, N_z


def rouwenhorst(n, rho, sigma):
    """Rouwenhorst's chain for ln z' = rho ln z + e, e ~ N(0, sigma^2), on n states (week 5, part 1).

    Returns the grid for ln z and the n x n transition matrix: the same numbers as quantecon.rouwenhorst,
    written out so that the template has no dependency beyond numpy.
    """
    p = (1 + rho) / 2
    Pi = np.array([[p, 1 - p], [1 - p, p]])  # the two-state chain
    for k in range(3, n + 1):  # one state more each round
        big = np.zeros((k, k))
        big[:-1, :-1] += p * Pi
        big[:-1, 1:] += (1 - p) * Pi
        big[1:, :-1] += (1 - p) * Pi
        big[1:, 1:] += p * Pi
        big[1:-1] /= 2  # the middle rows were added twice
        Pi = big
    psi = sigma * np.sqrt((n - 1) / (1 - rho**2))  # the grid matches the unconditional variance
    return np.linspace(-psi, psi, n), Pi


def stationary_distribution(Pi):
    """The stationary distribution of a Markov chain: lam = Pi' lam with sum(lam) = 1 (week 4)."""
    n = Pi.shape[0]
    A = np.vstack([Pi.T - np.eye(n), np.ones(n)])  # n equations of the fixed point, plus the normalization
    b = np.zeros(n + 1)
    b[-1] = 1.0
    lam = np.linalg.lstsq(A, b, rcond=None)[0]  # the system is consistent, least squares returns the solution
    return lam


def make_grids(amin, par, mpar):
    """The income chain on N_z Rouwenhorst states and the quadratically spaced asset grid on [amin, amax]."""
    lnz, Pi = rouwenhorst(mpar.nz, par.rho, par.sig_eps)
    s = np.linspace(0.0, 1.0, mpar.na)  # N_a equidistant points on [0, 1]
    a = amin + (mpar.amax - amin) * s**2  # squared: dense near amin, sparse near amax
    return Grids(a=a, z=np.exp(lnz), Pi=Pi, lam_z=stationary_distribution(Pi))
