# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Jinja2==3.1.6",
#   "Markdown==3.8.2",
# ]
# ///
"""Build the Ralph public pages."""

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
WHATS_NEW_PATH = ROOT / "content" / "ralph-whats-new.toml"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "weekly-ralph"
RALPH_OUTPUT_DIR = ROOT / "ralph"
SITE_URL = "https://bigskyai.ai"

# Static Ralph subpages rendered alongside the landing page:
# output directory name under ralph/ -> template filename.
RALPH_SUBPAGES = {
    "how-it-works": "ralph-how-it-works.html",
    "whats-new": "ralph-whats-new.html",
}

# Every public page path, for the generated sitemap. Root-level SEO
# artifacts (sitemap.xml, robots.txt) are built from SITE_URL so a future
# domain change stays a one-line edit.
STATIC_SITE_PATHS = (
    "",
    "about/",
    "ralph/",
    "ralph/how-it-works/",
    "ralph/whats-new/",
    "strummer/",
    "powbot/",
    "firetower/",
)


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


def load_whats_new() -> list[dict]:
    with WHATS_NEW_PATH.open("rb") as handle:
        entries = tomllib.load(handle)["entries"]
    for entry in entries:
        published = date.fromisoformat(entry["date"])
        entry["display_date"] = (
            f"{published:%B} {published.day}, {published.year}"
        )
    return sorted(entries, key=lambda item: item["date"], reverse=True)


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


def build_sitemap(issues: list[dict]) -> str:
    entries: list[str] = []
    for path in STATIC_SITE_PATHS:
        entries.append(
            "  <url>\n"
            f"    <loc>{html.escape(f'{SITE_URL}/{path}')}</loc>\n"
            "  </url>"
        )
    for issue in issues:
        entries.append(
            "  <url>\n"
            f"    <loc>{html.escape(issue['url'])}</loc>\n"
            f"    <lastmod>{issue['published']}</lastmod>\n"
            "  </url>"
        )
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            *entries,
            "</urlset>",
            "",
        ]
    )


def build_robots() -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "",
            f"Sitemap: {SITE_URL}/sitemap.xml",
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
        if destination.exists():
            shutil.rmtree(destination)
        return

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
            issue_template.render(issue=issue, site_url=SITE_URL),
            encoding="utf-8",
        )

    archive_template = environment.get_template("weekly-ralph-archive.html")
    (destination / "index.html").write_text(
        archive_template.render(issues=issues, site_url=SITE_URL),
        encoding="utf-8",
    )
    (destination / "feed.xml").write_text(build_rss(issues), encoding="utf-8")


def build_ralph(
    destination: Path,
    issues: list[dict],
    whats_new: list[dict],
) -> None:

    environment = create_environment()
    destination.mkdir(parents=True, exist_ok=True)
    source_assets = RALPH_OUTPUT_DIR / "assets"
    destination_assets = destination / "assets"
    if source_assets.resolve() != destination_assets.resolve():
        shutil.copytree(source_assets, destination_assets, dirs_exist_ok=True)

    context = {
        "issues": issues,
        "site_url": SITE_URL,
        "whats_new": whats_new,
    }

    template = environment.get_template("ralph-landing.html")
    (destination / "index.html").write_text(
        template.render(**context),
        encoding="utf-8",
    )

    for slug, template_name in RALPH_SUBPAGES.items():
        subpage_template = environment.get_template(template_name)
        subpage_dir = destination / slug
        subpage_dir.mkdir(parents=True, exist_ok=True)
        (subpage_dir / "index.html").write_text(
            subpage_template.render(**context),
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
    whats_new = load_whats_new()

    if args.check:
        with tempfile.TemporaryDirectory(prefix="weekly-ralph-") as temporary:
            expected_root = Path(temporary)
            expected_weekly_ralph = expected_root / "weekly-ralph"
            expected_ralph = expected_root / "ralph"
            build_weekly_ralph(expected_weekly_ralph, issues)
            build_ralph(expected_ralph, issues, whats_new)
            differences = []
            if expected_weekly_ralph.exists() or OUTPUT_DIR.exists():
                if expected_weekly_ralph.exists() and OUTPUT_DIR.exists():
                    differences.extend(
                        compare_directories(
                            expected_weekly_ralph,
                            OUTPUT_DIR,
                        )
                    )
                elif expected_weekly_ralph.exists() != OUTPUT_DIR.exists():
                    differences.append(
                        "weekly-ralph output presence does not match the build"
                    )
            differences.extend(
                compare_directories(expected_ralph, RALPH_OUTPUT_DIR)
            )
        for name, content in (
            ("sitemap.xml", build_sitemap(issues)),
            ("robots.txt", build_robots()),
        ):
            committed = ROOT / name
            if not committed.exists():
                differences.append(f"missing generated file: {name}")
            elif committed.read_text(encoding="utf-8") != content:
                differences.append(f"stale generated file: {name}")
        if differences:
            raise SystemExit("\n".join(differences))
        print("Ralph and Weekly Ralph generated output is current.")
        return

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    build_weekly_ralph(OUTPUT_DIR, issues)
    build_ralph(RALPH_OUTPUT_DIR, issues, whats_new)
    (ROOT / "sitemap.xml").write_text(build_sitemap(issues), encoding="utf-8")
    (ROOT / "robots.txt").write_text(build_robots(), encoding="utf-8")
    print(
        f"Built Ralph landing page, {len(RALPH_SUBPAGES)} subpage(s), "
        f"{len(whats_new)} What's-new entrie(s), "
        f"{len(issues)} Weekly Ralph issue(s), sitemap.xml, and robots.txt."
    )


if __name__ == "__main__":
    main()
