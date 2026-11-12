"""Figures and tables of the write-up, written to output/ by the launch file.

Every number that appears in the write-up is written here, to a .tex file that the write-up \\input's. Nothing
is typed into the text by hand.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no window, only files
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.aggregation import lorenz_curve  # noqa: E402

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def wealth_figure(lam, gri, path):
    """Two panels: the distribution of wealth at the equilibrium, and its Lorenz curve."""
    lam_a = lam.sum(axis=1)  # the marginal distribution over assets
    pop, wealth, gini = lorenz_curve(lam, gri)
    fig, (left, right) = plt.subplots(1, 2, figsize=(6.4, 2.6))
    edges = np.arange(0, 61, 1.0)  # bins of width one, as in the session 6 figures
    cdf = np.interp(edges, gri.a, np.cumsum(lam_a))  # the distribution function, read off between grid points
    cdf[0] = 0.0  # the first bin includes the mass at the limit
    mass = np.diff(cdf)
    left.bar(edges[:-1], mass, width=1.0, align="edge", color="#4c72b0", edgecolor="white", linewidth=0.3)
    left.text(0.97, 0.92, f"{100 * lam_a[0]:.1f} percent at $a = 0$", ha="right", transform=left.transAxes)
    left.set_xlim(0, 60)
    left.set_xlabel("assets $a$")
    left.set_ylabel("share of households per unit of $a$")
    left.set_title("Wealth distribution", loc="left")
    right.plot(pop, wealth, color="#4c72b0", label=f"Lorenz curve, Gini {gini:.2f}")
    right.plot([0, 1], [0, 1], color="#999999", linewidth=0.8, label="equality")
    right.set_xlabel("population share")
    right.set_ylabel("wealth share")
    right.set_title("Lorenz curve", loc="left")
    right.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def equilibrium_table(rows, path):
    """A booktabs table from (label, value, format) rows, to be \\input into the write-up."""
    lines = ["\\begin{tabular}{lr}", "\\toprule", "Statistic & Value \\\\", "\\midrule"]
    for label, value, fmt in rows:
        lines.append(f"{label} & {format(value, fmt)} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def numbers_file(numbers, path):
    """One LaTeX macro per number, so that the text of the write-up can cite results without retyping them."""
    lines = [f"\\newcommand{{\\{name}}}{{{format(value, fmt)}}}" for name, value, fmt in numbers]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
