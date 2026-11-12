"""setup_project.py: sets up the final project in your course repository. Run it once, from anywhere:

    python final_project/setup_project.py

What it does, in this order (each step says whether it worked, and what to do if not):

  1. checks that final_project/ sits inside your git repository
  2. moves the repository-wide settings to the root of the repository: .pre-commit-config.yaml (the hooks),
     pyproject.toml (black and pytest), .vscode/ (format on save), .github/workflows/ (the check on GitHub)
  3. creates the conda environment compmacro-project from environment.yml (or updates it)
  4. installs the pre-commit hook, so that every commit is formatted
  5. runs run_all.py and the smoke test once: if both pass, everything works

Running it again is harmless: what is already done is skipped. Options:
    --skip-env   do not create or update the conda environment (use the Python you started this with)
    --skip-run   do not run run_all.py and the test
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ENV_NAME = "compmacro-project"
HERE = Path(__file__).resolve().parent  # final_project/
ROOT_FILES = HERE / "repo_root_files"  # what goes to the root of the repository
NEEDED = ["numpy", "scipy", "matplotlib", "pytest", "pre_commit"]  # import names, for the case without conda
PIP_NAMES = {"pre_commit": "pre-commit"}

results = []  # (step, ok, message)


def say(text):
    print(text, flush=True)


def record(step, ok, message=""):
    results.append((step, ok, message))
    say(f"  [{'ok' if ok else '!!'}] {step}" + (f": {message}" if message else ""))


def run(cmd, **kwargs):
    """Run a command, show its output, return True if it succeeded."""
    try:
        return subprocess.run(cmd, **kwargs).returncode == 0
    except (FileNotFoundError, OSError) as err:
        say(f"       could not start {cmd[0]}: {err}")
        return False


# 1. Where are we


def find_repository():
    say("\n1. The repository")
    git = shutil.which("git")
    if git is None:
        record("git", False, "git is not on the PATH. Install Git (it comes with GitHub Desktop).")
        return None
    out = subprocess.run([git, "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, text=True)
    if out.returncode != 0:
        record(
            "repository",
            False,
            f"{HERE} is not inside a git repository. Unzip the template into your course repository, so "
            "that the folder final_project/ sits next to your problem sets, and run this again.",
        )
        return None
    root = Path(out.stdout.strip()).resolve()
    record("repository", True, str(root))
    if HERE.name != "final_project" or HERE.parent != root:
        say(f"       note: the project is at {HERE.relative_to(root)}, the course expects final_project/")
    return root


# 2. The files at the root of the repository


def merge_vscode_settings(src, dst):
    """Add the template's settings to an existing settings.json; keep everything the student set."""
    try:
        theirs = json.loads(dst.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        alt = dst.with_name(dst.stem + ".final_project.json")
        shutil.copyfile(src, alt)
        return False, f"{dst.name} not readable (comments?); the template's are in {alt.name}, copy them in"
    ours = json.loads(src.read_text(encoding="utf-8"))
    added = [key for key in ours if key not in theirs]
    for key in added:
        theirs[key] = ours[key]
    if added:
        dst.write_text(json.dumps(theirs, indent=4) + "\n", encoding="utf-8")
    return True, ("added " + ", ".join(added)) if added else "already there"


def place_root_files(root):
    say("\n2. Settings at the root of the repository")
    if not ROOT_FILES.is_dir():
        record("root files", True, "already in place (repo_root_files/ is gone, nothing to move)")
        return
    for src in sorted(p for p in ROOT_FILES.rglob("*") if p.is_file()):
        rel = src.relative_to(ROOT_FILES)
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel.parts[0] == ".vscode" and dst.exists():
            ok, msg = merge_vscode_settings(src, dst) if rel.name == "settings.json" else (True, "kept yours")
            record(str(rel), ok, msg)
            continue
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            backup = dst.with_name(dst.name + ".bak")
            shutil.copyfile(dst, backup)
            record(str(rel), True, f"replaced, your old version is in {backup.name}")
        else:
            record(str(rel), True, "in place")
        shutil.copyfile(src, dst)
    shutil.rmtree(ROOT_FILES)


# 3. The environment


def find_conda():
    exe = os.environ.get("CONDA_EXE")
    if exe and Path(exe).exists():
        return exe
    return shutil.which("conda") or shutil.which("mamba")


def make_environment(skip):
    """Return the command that starts Python in the project's environment, or None."""
    say("\n3. The environment")
    if skip:
        record("environment", True, f"skipped (--skip-env), using {sys.executable}")
        return [sys.executable]
    conda = find_conda()
    if conda is None:
        say("       conda not found: installing what is missing into the Python you started this with")
        missing = []
        for mod in NEEDED:
            if subprocess.run([sys.executable, "-c", f"import {mod}"], capture_output=True).returncode != 0:
                missing.append(PIP_NAMES.get(mod, mod))
        if missing and not run([sys.executable, "-m", "pip", "install", *missing]):
            record("environment", False, "pip could not install " + " ".join(missing))
            return [sys.executable]
        record("environment", True, f"{sys.executable} (no conda; versions are pinned in environment.yml)")
        return [sys.executable]
    listing = subprocess.run([conda, "env", "list", "--json"], capture_output=True, text=True)
    try:
        exists = any(Path(p).name == ENV_NAME for p in json.loads(listing.stdout)["envs"])
    except (ValueError, KeyError):
        exists = False
    verb = "update" if exists else "create"
    say(f"       conda env {verb} -f environment.yml (a few minutes the first time)")
    ok = run([conda, "env", verb, "-n", ENV_NAME, "-f", str(HERE / "environment.yml")])
    record(f"conda environment {ENV_NAME}", ok, "" if ok else f"conda env {verb} failed, see above")
    return [conda, "run", "--no-capture-output", "-n", ENV_NAME, "python"]


# 4. The hook


def install_hook(python, root):
    say("\n4. The pre-commit hook")
    ok = run([*python, "-m", "pre_commit", "install", "--install-hooks"], cwd=root)
    record("pre-commit hook", ok, "every commit is now formatted" if ok else "pre-commit install failed")


# 5. Does it run


def run_project(python, root):
    say("\n5. run_all.py and the smoke test")
    ok = run([*python, str(HERE / "run_all.py")], cwd=root)
    record("run_all.py", ok, "wrote output/" if ok else "failed, see the error above")
    ok = run([*python, "-m", "pytest", "-q", str(HERE / "tests")], cwd=root)
    record("smoke test", ok, "passed" if ok else "failed, see above")


def main():
    args = set(sys.argv[1:])
    say("Setting up the final project")
    root = find_repository()
    if root is not None:
        place_root_files(root)
        python = make_environment("--skip-env" in args)
        install_hook(python, root)
        if "--skip-run" not in args:
            run_project(python, root)
    failed = [r for r in results if not r[1]]
    say("\n" + "-" * 78)
    if failed:
        say("Not done yet. Fix what is marked [!!] and run this script again:")
        for step, _, msg in failed:
            say(f"  - {step}: {msg}")
        say("If you are stuck, send the whole output of this script to your instructor.")
        sys.exit(1)
    say("Done. Next:")
    say("  1. In GitHub Desktop, commit and push, the new files at the root of the repository included.")
    say("  2. On GitHub, the Actions tab of your repository shows the check: it runs your project on a")
    say("     clean machine after every push. A green tick means it reproduces.")
    say(f"  3. In VS Code, select the interpreter {ENV_NAME} (Ctrl+Shift+P, 'Python: Select Interpreter').")
    say("  4. Replace src/, run_all.py and the write-up with your own project; keep the structure.")


if __name__ == "__main__":
    main()
