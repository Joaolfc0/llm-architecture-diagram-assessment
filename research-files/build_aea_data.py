"""
Build pipeline to feed AEA site data from evaluation outputs.

This script:
1) Syncs diagram assets from research-files/*/assets into aea/assets
2) Picks the latest JSON evaluation file per criterion/model/format
3) Rebuilds OUTPUTS and DIAGRAMS sections in aea/data.js
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


CRITERIA = [
    "accuracy",
    "clarity",
    "completeness",
    "consistency",
    "level_of_detail",
]

MODEL_LABELS = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
}


@dataclass(frozen=True)
class ProjectConfig:
    slug: str
    title: str
    description_file: str
    png_file: str
    text_file: str
    text_format: str
    diagram_id: str


PROJECTS: List[ProjectConfig] = [
    ProjectConfig(
        slug="geoserver",
        title="GeoServer Cloud",
        description_file="description.txt",
        png_file="gs_cloud_architecture_diagram.png",
        text_file="gs_cloud_architecture_diagram.svg",
        text_format="SVG",
        diagram_id="geoserver-cloud",
    ),
    ProjectConfig(
        slug="appwrite",
        title="Appwrite",
        description_file="description.txt",
        png_file="overview.drawio.png",
        text_file="overview.drawio.svg",
        text_format="SVG",
        diagram_id="appwrite",
    ),
    ProjectConfig(
        slug="spryker",
        title="Spryker",
        description_file="description.txt",
        png_file="container-stack.png",
        text_file="container-stack.drawio.xml",
        text_format="XML",
        diagram_id="spryker",
    ),
    ProjectConfig(
        slug="sentry",
        title="Sentry",
        description_file="description.txt",
        png_file="sentry.drawio.png",
        text_file="sentry.drawio.xml",
        text_format="XML",
        diagram_id="sentry",
    ),
    ProjectConfig(
        slug="magda-io",
        title="Magda-io",
        description_file="description.txt",
        png_file="magda.drawio.png",
        text_file="marketecture.svg",
        text_format="SVG",
        diagram_id="magda-io",
    ),
    ProjectConfig(
        slug="research-modifiability-pattern-experiment",
        title="Research Modifiability Pattern Experiment",
        description_file="description.txt",
        png_file="02_architecture-final.png",
        text_file="02_architecture-final_draw.io.xml",
        text_format="XML",
        diagram_id="research-modifiability-pattern-experiment",
    ),
]


def _escape_js_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )


def _to_js(value, indent: int = 0) -> str:
    space = " " * indent
    next_space = " " * (indent + 4)

    if isinstance(value, dict):
        lines = ["{"]
        items = list(value.items())
        for index, (key, item) in enumerate(items):
            serialized = _to_js(item, indent + 4)
            comma = "," if index < len(items) - 1 else ""
            lines.append(f"{next_space}{key}: {serialized}{comma}")
        lines.append(f"{space}}}")
        return "\n".join(lines)

    if isinstance(value, list):
        if not value:
            return "[]"
        lines = ["["]
        for index, item in enumerate(value):
            serialized = _to_js(item, indent + 4)
            comma = "," if index < len(value) - 1 else ""
            if "\n" in serialized:
                indented = "\n".join(
                    f"{next_space}{line}" if line else line
                    for line in serialized.splitlines()
                )
                lines.append(f"{indented}{comma}")
            else:
                lines.append(f"{next_space}{serialized}{comma}")
        lines.append(f"{space}]")
        return "\n".join(lines)

    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)

    if isinstance(value, bool):
        return "true" if value else "false"

    if value is None:
        return "null"

    return str(value)


def _latest_criterion_file(eval_dir: Path, criterion: str) -> Path | None:
    candidates = sorted(eval_dir.glob(f"{criterion}_*.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _sync_asset(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def _replace_const_array(data_js: str, const_name: str, body: str) -> str:
    pattern = rf"const {const_name} = \[(?:.|\n)*?\];"
    replacement = f"const {const_name} = [\n{body}\n];"
    updated, count = re.subn(pattern, lambda _m: replacement, data_js, count=1)
    if count != 1:
        raise RuntimeError(f"Could not replace const {const_name} in data.js")
    return updated


def build() -> None:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    aea_dir = repo_root / "aea"
    assets_dir = aea_dir / "assets"
    data_js_path = aea_dir / "data.js"

    outputs: List[Dict] = []
    diagrams: List[Dict] = []
    output_index = 1
    warnings: List[str] = []

    for project in PROJECTS:
        project_dir = script_dir / project.slug
        project_assets_dir = project_dir / "assets"
        project_evals_dir = project_dir / "evaluations"

        png_src = project_assets_dir / project.png_file
        text_src = project_assets_dir / project.text_file
        description_src = project_assets_dir / project.description_file

        if not png_src.exists() or not text_src.exists() or not description_src.exists():
            warnings.append(f"[{project.slug}] Missing asset/description file. Skipping project.")
            continue

        _sync_asset(png_src, assets_dir / project.png_file)
        _sync_asset(text_src, assets_dir / project.text_file)

        with open(description_src, "r", encoding="utf-8") as file:
            description = file.read().strip()

        project_output_ids: List[str] = []

        for model_key, model_label in MODEL_LABELS.items():
            for fmt in ("png", project.text_format.lower()):
                eval_dir = project_evals_dir / f"{model_key}_{fmt}"
                if not eval_dir.exists():
                    warnings.append(f"[{project.slug}] Missing evaluations dir: {eval_dir.name}")
                    continue

                for criterion in CRITERIA:
                    latest_file = _latest_criterion_file(eval_dir, criterion)
                    if latest_file is None:
                        warnings.append(f"[{project.slug}] Missing {model_key}_{fmt} for criterion {criterion}")
                        continue

                    payload = _load_json(latest_file)
                    parsed = payload.get("parsed_response")
                    if not parsed:
                        warnings.append(f"[{project.slug}] No parsed_response in {latest_file.name}")
                        continue

                    output_id = f"OUT_{output_index:03d}"
                    output_index += 1

                    diagram_path = (
                        f"assets/{project.png_file}"
                        if fmt == "png"
                        else f"assets/{project.text_file}"
                    )

                    outputs.append(
                        {
                            "id": output_id,
                            "model": model_label,
                            "format": fmt.upper(),
                            "criterion": parsed["criterion"],
                            "diagramPath": diagram_path,
                            "guidelines": parsed["guidelines"],
                        }
                    )
                    project_output_ids.append(output_id)

        diagrams.append(
            {
                "id": project.diagram_id,
                "title": project.title,
                "description": description,
                "imagePath": f"assets/{project.png_file}",
                "textualPath": f"assets/{project.text_file}",
                "textualFormat": project.text_format,
                "outputIds": project_output_ids,
            }
        )

    if not outputs:
        raise RuntimeError("No outputs were generated. Aborting data.js update.")

    with open(data_js_path, "r", encoding="utf-8") as file:
        data_js_content = file.read()

    project_description = _escape_js_string(diagrams[0]["description"])
    data_js_content = re.sub(
        r"const PROJECT_DESCRIPTION = `(?:.|\n)*?`;",
        lambda _m: f"const PROJECT_DESCRIPTION = `{project_description}`;",
        data_js_content,
        count=1,
    )

    outputs_body = ",\n".join(_to_js(output, 4) for output in outputs)
    diagrams_body = ",\n".join(_to_js(diagram, 4) for diagram in diagrams)

    data_js_content = _replace_const_array(data_js_content, "OUTPUTS", outputs_body)
    data_js_content = _replace_const_array(data_js_content, "DIAGRAMS", diagrams_body)

    with open(data_js_path, "w", encoding="utf-8") as file:
        file.write(data_js_content)

    print(f"Updated {data_js_path}")
    print(f"Generated outputs: {len(outputs)}")
    print(f"Generated diagrams: {len(diagrams)}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    build()

