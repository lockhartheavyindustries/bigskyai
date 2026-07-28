# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Jinja2==3.1.6",
#   "Markdown==3.8.2",
# ]
# ///
"""Build the Ralph landing page and The Weekly Ralph publication."""

from __future__ import annotations

import argparse
import html
import shutil
import tempfile
import tomllib
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown
from markupsafe import Markup


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "weekly-ralph"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "weekly-ralph"
RALPH_OUTPUT_DIR = ROOT / "ralph"
SITE_URL = "https://lockhartheavyindustries.github.io/bigskyai"


def load_issues() -> list[dict]:
    issues: list[dict] = []
    for path in sorted(CONTENT_DIR.glob("*.toml")):
        with path.open("rb") as handle:
            issue = tomllib.load(handle)
        published = date.fromisoformat(issue["published"])
        issue["display_date"] = (
            f"{published:%B} {published.day}, {published.year}"
        )
        issue["url"] = f"{SITE_URL}/weekly-ralph/issues/{issue['slug']}/"
        issues.append(issue)
    return sorted(issues, key=lambda item: item["issue"], reverse=True)


def render_markdown(value: str) -> Markup:
    return Markup(markdown(value.strip(), extensions=["sane_lists"]))


def build_rss(issues: list[dict]) -> str:
    items: list[str] = []
    for issue in issues:
        published = date.fromisoformat(issue["published"])
        item_title = (
            f"The Weekly Ralph · Issue {issue['issue']:03d}: {issue['title']}"
        )
        published_dt = datetime(
            published.year,
            published.month,
            published.day,
            12,
            tzinfo=timezone.utc,
        )
        items.append(
            "\n".join(
                [
                    "    <item>",
                    f"      <title>{html.escape(item_title)}</title>",
                    f"      <link>{html.escape(issue['url'])}</link>",
                    f"      <guid isPermaLink=\"true\">{html.escape(issue['url'])}</guid>",
                    f"      <pubDate>{format_datetime(published_dt)}</pubDate>",
                    f"      <description>{html.escape(issue['description'])}</description>",
                    "    </item>",
                ]
            )
        )
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "  <channel>",
            "    <title>The Weekly Ralph</title>",
            f"    <link>{SITE_URL}/weekly-ralph/</link>",
            "    <description>Unexpected, practical ways real people put an AI assistant to work.</description>",
            "    <language>en-us</language>",
            *items,
            "  </channel>",
            "</rss>",
            "",
        ]
    )


def create_environment() -> Environment:
    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["markdown"] = render_markdown
    return environment


def build_weekly_ralph(destination: Path, issues: list[dict]) -> None:
    if not issues:
        raise SystemExit("No Weekly Ralph issue source files found.")

    environment = create_environment()

    destination.mkdir(parents=True, exist_ok=True)
    source_assets = OUTPUT_DIR / "assets"
    destination_assets = destination / "assets"
    if source_assets.resolve() != destination_assets.resolve():
        shutil.copytree(source_assets, destination_assets, dirs_exist_ok=True)

    issue_template = environment.get_template("weekly-ralph-issue.html")
    for issue in issues:
        issue_dir = destination / "issues" / issue["slug"]
        issue_dir.mkdir(parents=True, exist_ok=True)
        (issue_dir / "index.html").write_text(
            issue_template.render(issue=issue),
            encoding="utf-8",
        )

    archive_template = environment.get_template("weekly-ralph-archive.html")
    (destination / "index.html").write_text(
        archive_template.render(issues=issues, site_url=SITE_URL),
        encoding="utf-8",
    )
    (destination / "feed.xml").write_text(build_rss(issues), encoding="utf-8")


def build_ralph(destination: Path, issues: list[dict]) -> None:
    if not issues:
        raise SystemExit("No Weekly Ralph issue source files found.")

    environment = create_environment()
    destination.mkdir(parents=True, exist_ok=True)
    source_assets = RALPH_OUTPUT_DIR / "assets"
    destination_assets = destination / "assets"
    if source_assets.resolve() != destination_assets.resolve():
        shutil.copytree(source_assets, destination_assets, dirs_exist_ok=True)

    template = environment.get_template("ralph-landing.html")
    (destination / "index.html").write_text(
        template.render(issues=issues, site_url=SITE_URL),
        encoding="utf-8",
    )


def compare_directories(expected: Path, actual: Path) -> list[str]:
    expected_files = {
        path.relative_to(expected)
        for path in expected.rglob("*")
        if path.is_file()
    }
    actual_files = {
        path.relative_to(actual)
        for path in actual.rglob("*")
        if path.is_file()
    }
    differences = [
        f"missing generated file: {path}"
        for path in sorted(expected_files - actual_files)
    ]
    differences.extend(
        f"unexpected generated file: {path}"
        for path in sorted(actual_files - expected_files)
    )
    for path in sorted(expected_files & actual_files):
        if (expected / path).read_bytes() != (actual / path).read_bytes():
            differences.append(f"stale generated file: {path}")
    return differences


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that committed output matches a fresh build.",
    )
    args = parser.parse_args()
    issues = load_issues()

    if args.check:
        with tempfile.TemporaryDirectory(prefix="weekly-ralph-") as temporary:
            expected_root = Path(temporary)
            expected_weekly_ralph = expected_root / "weekly-ralph"
            expected_ralph = expected_root / "ralph"
            build_weekly_ralph(expected_weekly_ralph, issues)
            build_ralph(expected_ralph, issues)
            differences = compare_directories(
                expected_weekly_ralph,
                OUTPUT_DIR,
            )
            differences.extend(
                compare_directories(expected_ralph, RALPH_OUTPUT_DIR)
            )
        if differences:
            raise SystemExit("\n".join(differences))
        print("Ralph and Weekly Ralph generated output is current.")
        return

    preserved_assets = OUTPUT_DIR / "assets"
    with tempfile.TemporaryDirectory(prefix="weekly-ralph-assets-") as temporary:
        backup = Path(temporary) / "assets"
        if preserved_assets.exists():
            shutil.copytree(preserved_assets, backup)
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)
        if backup.exists():
            shutil.copytree(backup, preserved_assets)
    build_weekly_ralph(OUTPUT_DIR, issues)
    build_ralph(RALPH_OUTPUT_DIR, issues)
    print(f"Built Ralph landing page and {len(issues)} Weekly Ralph issue(s).")


if __name__ == "__main__":
    main()
