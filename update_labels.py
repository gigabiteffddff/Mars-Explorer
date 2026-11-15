from pathlib import Path


root = Path(__file__).resolve().parent

replacements = {
    "Hazard zones — DEMO": "Hazard zones",
    "DEMO hazard — illustrative extent": "Hazard zone",
    "Mission route — DEMO": "Mission route",
    "DEMO route": "Navigation route",
    "DEMO": "Synthetic",
}

for name in (
    "map_layers.py",
    "fields.py",
    "config.py",
    "mars_geo.py",
):
    path = root / name

    if not path.is_file():
        continue

    original = path.read_text(encoding="utf-8")
    updated = original

    for old, new in replacements.items():
        updated = updated.replace(old, new)

    if updated != original:
        compile(updated, str(path), "exec")
        path.write_text(updated, encoding="utf-8")
        print(f"Updated: {name}")