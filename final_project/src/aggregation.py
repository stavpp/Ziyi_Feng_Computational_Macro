"""From the policy to the distribution: Young's method of session 6.

The lottery, the policy chain as a sparse matrix, its stationary distribution, and the aggregates read off it.
"""

import numpy as np
import scipy.sparse as sp


def lottery(G, gri):
    """For every policy value a'_im: the index l of the grid point below it, and the weight w_im on l + 1."""
    na = len(gri.a)
    l = np.clip(np.searchsorted(gri.a, G, side="right") - 1, 0, na - 2)  # a_l <= a'_im < a_{l+1}
    w = (G - gri.a[l]) / (gri.a[l + 1] - gri.a[l])
    return l, np.clip(w, 0.0, 1.0)  # exactly at the top of the grid, w would be 1 + 1e-16


def transition_matrix(G, gri):
    """The policy chain Q_g as a sparse matrix.

    Q[(i, m), (l, n)] = Pi[m, n] (1 - w_im) and Q[(i, m), (l + 1, n)] = Pi[m, n] w_im, zeros elsewhere.
    """
    na, nz = len(gri.a), len(gri.z)
    idx = np.arange(na * nz).reshape(nz, na).T  # idx[i, m] = i + m N_a: the row of state (a_i, z_m)
    l, w = lottery(G, gri)
    rows, cols, vals = [], [], []  # the triplets, collected column block by column block
    for m in range(nz):  # income today
        for n in range(nz):  # income tomorrow
            rows.append(idx[:, m])  # mass 1 - w_im goes to (a_l, z_n) ...
            cols.append(idx[l[:, m], n])
            vals.append(gri.Pi[m, n] * (1 - w[:, m]))
            rows.append(idx[:, m])  # ... and mass w_im to (a_{l+1}, z_n)
            cols.append(idx[l[:, m] + 1, n])
            vals.append(gri.Pi[m, n] * w[:, m])
    triplets = (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols)))
    return sp.csr_matrix(triplets, shape=(na * nz, na * nz))


def stationary_dist(Q, mpar, gri, lam0=None):
    """Iterate lam_{n+1} = Q' lam_n from the uniform distribution (or from lam0).

    Returns lam as an N_a x N_z table, and the iteration count.
    """
    n = Q.shape[0]
    lam = np.full(n, 1 / n) if lam0 is None else lam0.T.ravel()  # the start, as a vector in the order of idx
    QT = Q.T.tocsr()  # the transpose once, in the fast row format
    for it in range(1, mpar.maxiter + 1):
        lam_new = QT @ lam
        dist = np.max(np.abs(lam_new - lam))
        lam = lam_new
        if dist < mpar.crit_dist:
            break
    return lam.reshape(len(gri.z), len(gri.a)).T, it  # back to the (a, z) table


def mean_assets(lam, gri):
    """A = sum_{i, m} lam_im a_i, with lam as an N_a x N_z table."""
    return (lam * gri.a[:, None]).sum()


def lorenz_curve(lam, gri):
    """The Lorenz curve of wealth (cumulative population share, cumulative wealth share) and the Gini."""
    lam_a = lam.sum(axis=1)  # the marginal distribution over assets
    pop = np.concatenate([[0.0], np.cumsum(lam_a)])
    wealth = np.concatenate([[0.0], np.cumsum(lam_a * gri.a)])
    wealth = wealth / wealth[-1]
    gini = 1 - np.sum((pop[1:] - pop[:-1]) * (wealth[1:] + wealth[:-1]))  # one minus twice the area below
    return pop, wealth, gini
