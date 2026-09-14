"""CLI entrypoint: python -m cold_outreach.main --mode b2b --industry fintech --region India."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as `python src/cold_outreach/main.py` (no package install) by
# putting `src` on sys.path before importing the package.
_SRC_DIR = Path(__file__).resolve().parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from cold_outreach.runner import run_outreach  # noqa: E402


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the hyper-targeted cold outreach crew.")
    parser.add_argument("--mode", choices=["b2b", "b2c"], default="b2b", help="Outreach mode (default: b2b).")
    parser.add_argument("--industry", required=True, help="Target industry, e.g. 'fintech'.")
    parser.add_argument("--region", required=True, help="Target region, e.g. 'India'.")
    parser.add_argument("--seed", default="", help="Optional seed company/person hint to focus research.")
    parser.add_argument("--model", default=None, help="Optional OpenRouter model slug override.")
    return parser.parse_args()


def main() -> None:
    """Run the crew from CLI arguments and print a readable summary."""
    args = _parse_args()

    result = run_outreach(
        mode=args.mode,
        industry=args.industry,
        region=args.region,
        seed_hint=args.seed,
        model=args.model,
    )

    icp = result.icp
    angle = result.angle
    email = result.email

    print("\n=== ICP PROFILE ===")
    print(f"Name: {icp.name} ({icp.entity_type})")
    print(f"Title: {icp.title or '—'}")
    print(f"Industry: {icp.industry} | Size/Seniority: {icp.size_or_seniority}")
    print(f"Pain point: {icp.pain_point}")
    print(f"Confidence: {icp.confidence}")
    print("Evidence:")
    for ev in icp.evidence:
        print(f'  - "{ev.quote}" — {ev.source_url} ({ev.date or "n/a"})')

    print("\n=== OUTREACH ANGLE ===")
    print(f"Pain restated: {angle.pain_restated}")
    print(f"Matched offering: {angle.matched_offering}")
    print(f"Mechanism: {angle.mechanism}")
    print(f"Proof point: {angle.proof_point}")
    print(f"Angle: {angle.angle_one_liner}")

    print("\n=== COLD EMAIL ===")
    print(f"Subject: {email.subject}")
    print()
    print(email.body)
    print(f"\n(Word count: {email.word_count})")

    print("\n=== OUTPUT FILES ===")
    print(f"JSON: {result.json_path}")
    print(f"Markdown: {result.md_path}")


if __name__ == "__main__":
    main()
