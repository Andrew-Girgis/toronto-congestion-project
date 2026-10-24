"""Download dated snapshots of the configured open-data sources.

Usage: uv run python -m cordon.ingest [source_id ...]

Raw files are never modified after download. Each file is recorded in
data/manifest.csv with its resolved URL, retrieval time, size and SHA-256.
"""

import csv
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

from cordon import CONFIG, DATA

MANIFEST = DATA / "manifest.csv"
FIELDS = ["source_id", "package", "resource_name", "resource_id", "url", "file",
          "retrieved_at", "bytes", "sha256", "resource_last_modified", "licence"]


def resolve(client, base, src):
    """Return CKAN resource dicts for a source entry, failing loudly on a miss."""
    pkg = client.get(f"{base}/package_show", params={"id": src["package"]}).json()["result"]
    by_name = {r["name"]: r for r in pkg["resources"]}
    out = []
    for name in src.get("resources", []):
        if name not in by_name:
            raise KeyError(f"{src['package']}: resource {name!r} not found")
        out.append(by_name[name])
    for rule in src.get("match_format", []):
        hits = [r for r in pkg["resources"]
                if r["name"].startswith(rule["name_prefix"]) and r.get("format") == rule["format"]]
        if not hits:
            raise KeyError(f"{src['package']}: no {rule['format']} matching {rule['name_prefix']!r}")
        out.append(hits[0])
    return out


def download(client, url, dest):
    h = hashlib.sha256()
    n = 0
    with client.stream("GET", url) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
                h.update(chunk)
                n += len(chunk)
    return n, h.hexdigest()


def main(selected):
    cfg = yaml.safe_load((CONFIG / "sources.yaml").read_text())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_file = not MANIFEST.exists()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=httpx.Timeout(60, read=600), follow_redirects=True) as client, \
            open(MANIFEST, "a", newline="") as mf:
        writer = csv.DictWriter(mf, FIELDS)
        if new_file:
            writer.writeheader()
        for src in cfg["sources"]:
            if selected and src["source_id"] not in selected:
                continue
            outdir = DATA / "raw" / src["source_id"] / today
            outdir.mkdir(parents=True, exist_ok=True)
            for res in resolve(client, cfg["ckan_base"], src):
                url = res["url"]
                fname = Path(url.split("?")[0]).name
                dest = outdir / fname
                if dest.exists():
                    print(f"skip (exists) {dest.relative_to(DATA)}")
                    continue
                print(f"get {src['source_id']}: {res['name']} ...", flush=True)
                nbytes, digest = download(client, url, dest)
                writer.writerow({
                    "source_id": src["source_id"], "package": src["package"],
                    "resource_name": res["name"], "resource_id": res["id"], "url": url,
                    "file": str(dest.relative_to(DATA.parent)),
                    "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "bytes": nbytes, "sha256": digest,
                    "resource_last_modified": res.get("last_modified") or "",
                    "licence": "OGL-Toronto (UNVERIFIED per dataset)",
                })
                mf.flush()
                print(f"  {nbytes / 1e6:.1f} MB  sha256={digest[:12]}")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
