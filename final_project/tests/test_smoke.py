"""One smoke test: a number you know. It catches the change that broke everything.

    pytest

The baseline Aiyagari economy of the course has r* = 2.53 percent and K* = 7.57 (session 6, slide 21).
"""

from src.equilibrium import aiyagari_economy, stationary_equilibrium
from src.model import EconomicParameters, NumericalParameters


def test_aiyagari_equilibrium_matches_class():
    par, mpar = EconomicParameters(), NumericalParameters()
    eco = aiyagari_economy(par, mpar)
    r_star, agg, _ = stationary_equilibrium(eco, par, mpar, 0.0, 1 / par.beta - 1 - 1e-4)
    assert abs(r_star - 0.0253) < 2e-4
    assert abs(agg.A - 7.57) < 2e-2
    assert abs(agg.lam.sum() - 1.0) < 1e-10  # the distribution is a distribution
