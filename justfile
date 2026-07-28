build:
    uv run scripts/build_weekly_ralph.py

check: build
    uv run scripts/build_weekly_ralph.py --check
    uv run scripts/check_site.py

serve:
    python3 -m http.server 8000
