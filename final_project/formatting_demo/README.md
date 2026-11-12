# The formatting demo

`badly_formatted.py` runs, and it is hard to read: no spaces around operators, two-space indentation in one
function and four in the next, single and double quotes, two statements on one line, a 135-character line.
Nobody should fix this by hand. The formatter does it, and the pre-commit hook makes sure it is never forgotten.

## Try it

From the root of the repository, with the environment active (`conda activate compmacro-project`):

```
black final_project/formatting_demo/                        # formats the file in place
git diff final_project/formatting_demo/                     # what changed: layout only, the logic is untouched
python final_project/formatting_demo/badly_formatted.py     # runs exactly as before
git checkout -- final_project/formatting_demo/              # puts the ugly version back, to repeat the demo
```

With the hook installed (`setup_project.py` did that), the same happens on every commit without a
command: change one character in the file, `git add` and `git commit`, and the commit stops with
`files were modified by this hook`. The file is now formatted; `git add` it and commit again.

## What black changes

```python
# A deliberately badly formatted file, ...
import numpy as np


def utility(c, gamma=2.0):
    """CRRA utility, log utility for gamma = 1"""
    if gamma == 1:
        return np.log(c)
    return c ** (1 - gamma) / (1 - gamma)


def bisect(f, lo, hi, tol=1e-6):
    # find the root of f on [lo, hi] by bisection, f increasing
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


grid = np.linspace(0, 100, 200) ** 2 / 100
values = utility(grid + 1)
upper = grid[len(grid) // 2 :]
weights = [0.25, 0.5, 0.25]
root = bisect(lambda r: utility(1 + r, gamma=2.0) - utility(1.02, gamma=2.0), 0.0, 0.1, 1e-8)
summary = dict(
    root=root,
    utility_at_root=utility(1 + root),
    mean_utility_on_grid=values.mean(),
    grid_points=len(grid),
    tolerance=1e-8,
)
print("root %.6f, utility at the root %.6f" % (root, utility(1 + root)))
```

In words: one space around operators and after commas, none inside brackets, none around `=` in keyword
arguments; four spaces of indentation; two blank lines around top-level functions; double quotes; one statement
per line; `1E-8` becomes `1e-8`; a space after `#`; a line longer than `line-length = 110` (set in
`pyproject.toml` at the root of the repository) is split at its brackets, one argument per line with a
trailing comma. Nothing else: black never changes what the code does.
