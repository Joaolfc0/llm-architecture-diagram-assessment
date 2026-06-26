"""
Run all architecture evaluations using ChatGPT across all projects.
"""

import argparse
import subprocess
import sys
from pathlib import Path


PROJECTS = [
    "geoserver",
    "appwrite",
    "spryker",
    "sentry",
    "magda-io",
    "research-modifiability-pattern-experiment",
]


def build_command(script_path: Path, delay: int, criteria: list[str] | None) -> list[str]:
    command = [sys.executable, str(script_path), "--model", "chatgpt", "--delay", str(delay)]
    if criteria:
        command.extend(["--criteria", *criteria])
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all project evaluations using ChatGPT."
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=5,
        help="Delay in seconds passed to each project script (default: 5).",
    )
    parser.add_argument(
        "--criteria",
        nargs="+",
        choices=["accuracy", "clarity", "completeness", "consistency", "level_of_detail"],
        default=None,
        help="Optional criteria list to pass through to project scripts.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop immediately if one project run fails.",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    failures: list[str] = []

    print("=" * 80)
    print("RUN ALL PROJECTS - CHATGPT")
    print("=" * 80)

    for index, project in enumerate(PROJECTS, start=1):
        script_path = base_dir / project / "scripts" / "run_evaluation.py"
        if not script_path.exists():
            print(f"\n[{index}/{len(PROJECTS)}] {project}: script not found at {script_path}")
            failures.append(project)
            if args.stop_on_error:
                return 1
            continue

        command = build_command(script_path, args.delay, args.criteria)
        print("\n" + "-" * 80)
        print(f"[{index}/{len(PROJECTS)}] Running {project} with ChatGPT")
        print("-" * 80)
        print("Command:", " ".join(command))

        result = subprocess.run(command, cwd=script_path.parent)
        if result.returncode != 0:
            failures.append(project)
            print(f"{project}: FAILED (exit code {result.returncode})")
            if args.stop_on_error:
                return result.returncode
        else:
            print(f"{project}: OK")

    print("\n" + "=" * 80)
    if failures:
        print(f"Completed with failures in: {', '.join(failures)}")
        print("=" * 80)
        return 1

    print("All project runs completed successfully.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

