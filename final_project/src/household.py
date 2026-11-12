"""The household problem: the endogenous grid method of week 5.

One function per task: marginal utility and its inverse, one EGM step, and the loop that iterates the step
until the policy stops moving.
"""

import numpy as np


def uprime(c, par):
    """Marginal utility of CRRA utility u(c) = c^(1 - gamma) / (1 - gamma), that is u'(c) = c^(-gamma)."""
    return c ** (-par.gamma)


def uprime_inv(m, par):
    """The inverse of marginal utility: the c with u'(c) = m."""
    return m ** (-1 / par.gamma)


def egm_step(C, r, w, par, gri):
    """One step of the endogenous grid method: from the consumption policy C on the grid to the new policy."""
    R = 1 + r
    EMU = uprime(C, par) @ gri.Pi.T  # expected marginal utility tomorrow at every (a'_l, z_m)
    ctilde = uprime_inv(par.beta * R * EMU, par)  # (a) consumption today from the inverted Euler equation
    atilde = (ctilde + gri.a[:, None] - w * gri.z[None, :]) / R  # (b) today's assets, budget constraint
    Cnew = np.empty_like(C)  # (c) back to the grid, one income state at a time
    for m in range(len(gri.z)):
        Cnew[:, m] = np.interp(gri.a, atilde[:, m], ctilde[:, m])
        below = gri.a < atilde[0, m]  # poorer than the household that saves a' = a_1: the limit binds
        Cnew[below, m] = w * gri.z[m] + R * gri.a[below] - gri.a[0]  # consume everything down to a' = a_1
    return Cnew


def solve_household(r, w, par, mpar, gri, C0=None):
    """Iterate egm_step until the policy stops moving. Returns C, the savings policy G, and the count.

    C0: an optional starting guess for the policy, for example the solution at nearby prices (a warm start).
    """
    R = 1 + r
    if C0 is None:
        C = np.maximum(r * gri.a[:, None] + w * gri.z[None, :], 1e-6)  # guess: consume interest and income
    else:
        C = C0.copy()
    for it in range(1, mpar.maxiter + 1):
        Cnew = egm_step(C, r, w, par, gri)
        dist = np.max(np.abs(Cnew - C))  # largest change of the policy
        C = Cnew
        if dist < mpar.crit_pol:
            break
    G = w * gri.z[None, :] + R * gri.a[:, None] - C  # savings a' = w z + R a - c, N_a x N_z
    return C, G, it
