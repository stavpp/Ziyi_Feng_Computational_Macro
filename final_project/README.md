# Project title

*Computational Macro (HWS 2026), University of Mannheim. Final project of: your name.*

**What this project does.** One paragraph: the model, the extension, the main result. The template solves the
Aiyagari (1994) economy of session 6 with the methods of the course (endogenous grid method, Young's method,
bisection on the interest rate) and reports the stationary equilibrium, the wealth distribution, and a Monte
Carlo check with its standard error across seeds. Replace this paragraph and the code in `src/` with your own
project and keep the structure.

## Set up, once

Unzip the template into your course repository, so that the folder `final_project/` sits next to your problem
sets. Then, in a terminal in the repository (in VS Code: Terminal, New Terminal):

```
python final_project/setup_project.py
```

It moves the repository-wide settings to the root of the repository (the pre-commit hooks, the black and pytest
settings, the VS Code settings, the check on GitHub), creates the conda environment `compmacro-project` from
`environment.yml`, installs the pre-commit hook, and runs the project and the smoke test once. Each step says
whether it worked and what to do if not; running it again is harmless. Then commit and push everything, and in
VS Code select the interpreter `compmacro-project` (Ctrl+Shift+P, "Python: Select Interpreter").

On another computer, after cloning: `python final_project/setup_project.py` again.

## How to run

From the root of the repository:

```
conda activate compmacro-project
python final_project/run_all.py      # every figure and table of the write-up, about 15 seconds
pytest                               # the smoke test, about 2 seconds
```

`run_all.py` writes `output/figures/wealth.pdf`, `output/tables/equilibrium.tex`, `output/tables/numbers.tex`
and `output/log.txt`. The write-up in `writeup/project.tex` includes these files, compile it with `pdflatex`
after the run. Nothing in `output/` is edited by hand.

## Structure

```
<your repository>/
├── .pre-commit-config.yaml      the hooks that run before every commit           ┐ moved here by
├── pyproject.toml               settings of black (line length 110) and pytest   │ setup_project.py,
├── .vscode/                     format on save                                   │ they apply to the
├── .github/workflows/           the check on GitHub, after every push            ┘ whole repository
├── (your problem sets)
└── final_project/
    ├── README.md                what, how to run, how long, what comes out where
    ├── setup_project.py         the setup above
    ├── run_all.py               the launch file: every figure and table from scratch, every seed set here
    ├── environment.yml          the pinned environment
    ├── src/                     functions only, nothing runs on import
    │   ├── model.py             parameters, grids, the income process
    │   ├── household.py         the endogenous grid method
    │   ├── aggregation.py       the lottery, the policy chain, the stationary distribution
    │   ├── simulation.py        the Monte Carlo panel, with the seed as an argument
    │   ├── equilibrium.py       one wrapper for Huggett and Aiyagari
    │   └── figures.py           writes the figures and the .tex tables
    ├── tests/
    │   └── test_smoke.py        one number you know: r* = 2.53 percent
    ├── output/                  written by run_all.py, never edited
    │   ├── figures/
    │   └── tables/
    ├── writeup/
    │   └── project.tex          five to eight pages, \input and \includegraphics from output/
    └── formatting_demo/         a badly formatted file, to see what black does (delete it in your project)
```

## Formatting, and the pre-commit hook

The code is formatted with `black` (settings in `pyproject.toml`), and a git hook runs it before every commit so
that nobody has to think about it. `setup_project.py` installed the hook. From now on `git commit` runs the hooks
first. A hook that changed a file stops the commit and leaves the file formatted: `git add` it and commit again.
Commits from GitHub Desktop or VS Code run the hooks too. In VS Code, the settings in `.vscode/` format on save
with the Black Formatter extension, so the hook rarely has anything left to do. To see the formatter at work,
`formatting_demo/README.md`.

## The check on GitHub

After every push that touches the project, GitHub runs it on a clean machine (`.github/workflows/`): the hooks on
every file of `final_project/`, `run_all.py` from scratch in the environment of `environment.yml`, the smoke
test, and `pdflatex` on the write-up. The result is the tick or the cross next to your commit, and the Actions
tab of your repository shows the details. A green tick means your project reproduces on a machine that is not
yours. A yellow warning means the tables you committed differ from those the code produces now: run `run_all.py`,
compile the write-up, commit both. Each run keeps the reproduced `output/` and write-up for download (Artifacts).

## Reproducibility

- **Environment:** `environment.yml` pins Python and the packages. Before you submit, record the exact versions
  you used with `conda env export --from-history` and commit the file.
- **Seeds:** every random number comes from a generator created from a seed in `run_all.py` (`SEEDS`), passed
  as an argument. Simulated numbers are reported with their standard error across seeds.
- **One command:** `python final_project/run_all.py` produces every file the write-up includes. The check on
  GitHub runs exactly that on a clean machine after every push.

## Checklist before you submit

- [ ] the check on GitHub is green for your last commit
- [ ] `writeup/project.pdf` is in the repository, compiled from the current `output/`, no retyped numbers
- [ ] this README says what, how to run, how long, and what comes out where
- [ ] the note on AI use below is filled in

## AI use

Which tools, for what. The rule of the syllabus applies: you must be able to explain every line.
