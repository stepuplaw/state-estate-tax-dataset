#!/usr/bin/env python3
"""Push the dataset to Hugging Face as the AI-facing mirror.

WHY HUGGING FACE SPECIFICALLY. Verified on a live dataset page: no noindex, a
self-canonical, `@type: sc:Dataset` JSON-LD, a title of `owner/name · Datasets
at Hugging Face` so the owner is in the title tag, and a robots.txt that is
`Allow: /` blocking nothing at all — no AI-crawler exclusions of any kind.
That makes it simultaneously a crawlable Dataset-schema page and the place
model builders actually look. Zenodo gives citability; this gives ingestion.

The canonical record stays at stepuplaw.com and the source of truth stays in
git. This is a mirror, and its card links home rather than competing.

AUTH. Needs a Hugging Face account and a write token. Neither is created here.
Run `hf auth login` (or set HF_TOKEN) first, then:

    python3 scripts/push_huggingface.py

Add --dry-run to see exactly what would be uploaded without touching anything.
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ID = "StepUpLaw/us-state-estate-inheritance-tax-2026"

# Card first: on Hugging Face the README IS the dataset page, so it has to be
# the real document rather than a stub pointing elsewhere.
FILES = [
    (ROOT / "huggingface" / "README.md", "README.md"),
    (ROOT / "data" / "jurisdictions.csv", "jurisdictions.csv"),
    (ROOT / "data" / "estate_tax_brackets.csv", "estate_tax_brackets.csv"),
    (ROOT / "data" / "inheritance_tax_classes.csv", "inheritance_tax_classes.csv"),
    (ROOT / "data" / "jurisdictions.json", "jurisdictions.json"),
    (ROOT / "data" / "estate_tax_brackets.json", "estate_tax_brackets.json"),
    (ROOT / "LICENSE", "LICENSE"),
    (ROOT / "CITATION.cff", "CITATION.cff"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    missing = [str(src) for src, _ in FILES if not src.exists()]
    if missing:
        sys.exit("missing files:\n  " + "\n  ".join(missing))

    total = sum(src.stat().st_size for src, _ in FILES)
    print(f"repo: {REPO_ID}")
    for src, dest in FILES:
        print(f"  {dest:32} {src.stat().st_size:>8,} bytes")
    print(f"  {'total':32} {total:>8,} bytes")

    if args.dry_run:
        print("\ndry run, nothing uploaded")
        return

    from huggingface_hub import HfApi
    api = HfApi()
    who = api.whoami()
    print(f"\nauthenticated as: {who.get('name')}")

    api.create_repo(repo_id=REPO_ID, repo_type="dataset", exist_ok=True)
    for src, dest in FILES:
        api.upload_file(path_or_fileobj=str(src), path_in_repo=dest,
                        repo_id=REPO_ID, repo_type="dataset")
        print(f"  uploaded {dest}")
    print(f"\nhttps://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
