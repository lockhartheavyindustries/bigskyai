"""Check Ralph's public pages for broken local links and privacy leaks."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIRS = (ROOT / "ralph", ROOT / "weekly-ralph")
STATIC_PAGES = (ROOT / "index.html", ROOT / "strummer" / "index.html")
GOATCOUNTER_MARKER = (
    'data-goatcounter="https://bigskyai.goatcounter.com/count"'
)
DENYLIST = (
    "Mellissa",
    "Colleen",
    "Chris",
    "Jeff",
    "Steve",
    "+1208",
    "+1406",
    "+1425",
)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"] or "")
        if tag in {"img", "script", "source"} and attributes.get("src"):
            self.links.append(attributes["src"] or "")
        if tag == "link" and attributes.get("href"):
            self.links.append(attributes["href"] or "")


def resolve_local_link(source: Path, link: str) -> Path | None:
    parsed = urlparse(link)
    if parsed.scheme or parsed.netloc or link.startswith("#"):
        return None
    clean_path = unquote(parsed.path)
    target = (source.parent / clean_path).resolve()
    if clean_path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def main() -> None:
    errors: list[str] = []
    html_files = sorted(
        path
        for public_dir in PUBLIC_DIRS
        for path in public_dir.rglob("*.html")
    )
    if not html_files:
        raise SystemExit("No generated Ralph HTML found.")

    tracked_pages = [*STATIC_PAGES, *html_files]
    for path in tracked_pages:
        text = path.read_text(encoding="utf-8")
        if text.count(GOATCOUNTER_MARKER) != 1:
            errors.append(
                f"{path.relative_to(ROOT)} must contain exactly one "
                "GoatCounter beacon"
            )

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        for private_value in DENYLIST:
            if private_value.lower() in text.lower():
                errors.append(f"{path.relative_to(ROOT)} contains private value: {private_value}")

        required = (
            '<meta name="description"',
            '<meta property="og:title"',
            '<link rel="canonical"',
        )
        for marker in required:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)} missing {marker}")
        if "&lt;p&gt;" in text:
            errors.append(
                f"{path.relative_to(ROOT)} contains escaped Markdown HTML"
            )

        parser = LinkParser()
        parser.feed(text)
        for link in parser.links:
            target = resolve_local_link(path, link)
            if target is not None and not target.exists():
                errors.append(
                    f"{path.relative_to(ROOT)} has broken link {link!r}"
                )

    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"Checked {len(html_files)} Ralph and Weekly Ralph HTML pages "
        f"and analytics coverage on {len(tracked_pages)} public pages."
    )


if __name__ == "__main__":
    main()
