#!/usr/bin/env python3
"""Validate the repository-local coordination manifest."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / ".coordination/project.json").read_text())
schema = json.loads((ROOT / ".coordination/project-manifest.schema.json").read_text())
Draft202012Validator(schema).validate(manifest)

for field in ("briefing", "instructions"):
    path = ROOT / manifest[field]
    if not path.is_file():
        raise SystemExit(f"missing coordination {field}: {manifest[field]}")

for flag in ("issue_required", "branch_required", "pull_request_required"):
    if manifest["work"].get(flag) is not True:
        raise SystemExit(f"coordination work.{flag} must be true")

if not manifest["verification"].get("commands"):
    raise SystemExit("coordination verification.commands must be nonempty")

print(f"coordination contract valid for {manifest['project']}")
