#!/usr/bin/env python3
"""Anonymize participant emails in study CSVs for the replication package.

Replaces Expert_ID (email) with P001..Pnnn and Submission_ID / Participant_ID
with the matching participant code. Keeps a private mapping file (gitignored).

Run from research-files/analysis-csv/:
    python anonymize_participants.py

Re-run only after restoring originals from _private_originals/.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
BACKUP_DIR = ROOT / "_private_originals"
MAP_FILE = ROOT / "participant_id_map_PRIVATE.csv"

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")

FILES = [
    ROOT / "llm-assesment-v2 - participant_demographics.csv",
    ROOT / "llm-assesment-v2 - gt_scores.csv",
    ROOT / "llm-assesment-v2 - pairwise_preferences.csv",
    ROOT / "ground-truth" / "selected_experts.csv",
]

NOTEBOOK = ROOT / "ground-truth" / "build_ground_truth.ipynb"


def backup_once(path: Path) -> None:
    BACKUP_DIR.mkdir(exist_ok=True)
    dest = BACKUP_DIR / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(path, dest)
        print(f"  backed up -> {dest.relative_to(ROOT)}")


def build_mapping(demo: pd.DataFrame) -> tuple[dict[str, str], dict[str, str]]:
    """Return (email -> P00X, original_submission_id -> P00X)."""
    emails = sorted(set(demo["Expert_ID"].astype(str).str.strip()))
    email_to_pid = {e: f"P{i:03d}" for i, e in enumerate(emails, start=1)}

    sub_to_pid: dict[str, str] = {}
    for _, row in demo.iterrows():
        pid = email_to_pid[str(row["Expert_ID"]).strip()]
        for col in ("Submission_ID", "Participant_ID"):
            if col in row and pd.notna(row[col]):
                sub_to_pid[str(row[col]).strip()] = pid
    return email_to_pid, sub_to_pid


def replace_emails_in_text(text: str, email_to_pid: dict[str, str]) -> str:
    if not isinstance(text, str) or not text:
        return text
    out = text
    for email in sorted(email_to_pid, key=len, reverse=True):
        out = out.replace(email, email_to_pid[email])
    return out


def anonymize_csv(path: Path, email_to_pid: dict[str, str], sub_to_pid: dict[str, str]) -> None:
    df = pd.read_csv(path)
    id_cols = [c for c in df.columns if c in ("Expert_ID", "Submission_ID", "Participant_ID", "kept", "discarded")]
    for col in id_cols:
        if col in ("kept", "discarded"):
            df[col] = df[col].apply(lambda v: replace_emails_in_text(v, email_to_pid) if pd.notna(v) else v)
        elif col == "Expert_ID":
            df[col] = df[col].astype(str).str.strip().map(email_to_pid)
        elif col in ("Submission_ID", "Participant_ID"):
            df[col] = df[col].astype(str).str.strip().map(lambda s: sub_to_pid.get(s, s))
    df.to_csv(path, index=False)
    print(f"  anonymized {path.name}")


def update_notebook_tiebreakers(email_to_pid: dict[str, str]) -> None:
    import nbformat

    nb = nbformat.read(NOTEBOOK, as_version=4)
    for cell in nb.cells:
        if cell.cell_type != "code" or "MANUAL_TIEBREAKERS" not in cell.source:
            continue
        src = cell.source
        for email, pid in email_to_pid.items():
            src = src.replace(f'"{email}"', f'"{pid}"')
        cell.source = src
        nbformat.write(nb, NOTEBOOK)
        print(f"  updated MANUAL_TIEBREAKERS in {NOTEBOOK.name}")
        return


def verify_no_emails() -> list[str]:
    leaks = []
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        found = EMAIL_RE.findall(text)
        if found:
            leaks.append(f"{path.name}: {sorted(set(found))}")
    return leaks


def main() -> None:
    demo_path = ROOT / "llm-assesment-v2 - participant_demographics.csv"
    print("Backing up originals (first run only)...")
    for f in FILES:
        if f.exists():
            backup_once(f)

    demo = pd.read_csv(BACKUP_DIR / demo_path.relative_to(ROOT) if (BACKUP_DIR / demo_path.relative_to(ROOT)).exists() else demo_path)
    # Use backup for stable mapping if re-running after partial edit
    src_demo = BACKUP_DIR / demo_path.relative_to(ROOT)
    if src_demo.exists():
        demo = pd.read_csv(src_demo)

    email_to_pid, sub_to_pid = build_mapping(demo)

    mapping_df = pd.DataFrame(
        [{"participant_id": pid, "original_expert_id": email} for email, pid in email_to_pid.items()]
    )
    mapping_df.to_csv(MAP_FILE, index=False)
    print(f"Wrote mapping ({len(email_to_pid)} participants) -> {MAP_FILE.name}")

    print("Anonymizing CSVs...")
    for f in FILES:
        if f.exists():
            anonymize_csv(f, email_to_pid, sub_to_pid)

    if NOTEBOOK.exists():
        update_notebook_tiebreakers(email_to_pid)

    leaks = verify_no_emails()
    if leaks:
        print("WARNING: emails still found:")
        for line in leaks:
            print(" ", line)
    else:
        print("OK: no email addresses remain in CSV files.")


if __name__ == "__main__":
    main()
