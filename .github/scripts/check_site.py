"""Quick health checks for the KOGA website.

GitHub Actions runs this file every time the site changes.
If any check fails, the script exits with an error and the run turns red.
You can also run it on your own computer with:  python3 .github/scripts/check_site.py
"""
import os
import re
import sys

PAGE = "index.html"
MAX_MB = 5  # keep the page light so it opens quickly on phones

problems = []
passed = []

# 1. The files the site needs must all be there.
required = [PAGE, ".nojekyll", "favicon.ico", "favicon-32.png", "favicon-192.png",
            "apple-touch-icon.png", "koga-link-preview.jpg"]
missing = [f for f in required if not os.path.exists(f)]
if missing:
    problems.append("Missing files: " + ", ".join(missing))
else:
    passed.append(f"All {len(required)} required files are present")

html = open(PAGE, encoding="utf-8").read()

# 2. Every local file the page points to must exist (catches typos and deleted images).
refs = set(re.findall(r'(?:href|src)="([^"]+)"', html))
local = sorted(r for r in refs
               if not r.startswith(("http", "data:", "#", "mailto:", "tel:", "${", "javascript:")))
broken = [r for r in local if not os.path.exists(r.split("?")[0])]
if broken:
    problems.append("Links to files that don't exist: " + ", ".join(broken))
else:
    passed.append(f"All {len(local)} local links point to real files")

# 3. No '?v=' cache-busting on links (house rule: links stay clean).
if "?v=" in html:
    problems.append("Found a '?v=' link. Links should stay clean.")
else:
    passed.append("No '?v=' links")

# 4. Page size.
mb = os.path.getsize(PAGE) / 1024 / 1024
if mb > MAX_MB:
    problems.append(f"{PAGE} is {mb:.1f} MB, over the {MAX_MB} MB limit")
else:
    passed.append(f"{PAGE} is {mb:.2f} MB (limit {MAX_MB} MB)")

# 5. The WhatsApp link preview needs these tags.
for tag in ("og:title", "og:description", "og:image"):
    if f'property="{tag}"' not in html:
        problems.append(f"Missing the {tag} tag, so WhatsApp previews may break")
if not any(p.startswith("Missing the og") for p in problems):
    passed.append("WhatsApp link preview tags are in place")

# Write a little report. On GitHub it shows on the run's summary page.
report = ["## KOGA website checks", ""]
report += [f"- ✅ {p}" for p in passed]
report += [f"- ❌ {p}" for p in problems]
print("\n".join(report))
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")

sys.exit(1 if problems else 0)
