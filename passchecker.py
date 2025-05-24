#!/usr/bin/env python3






import argparse
import json
import logging
import re
import sys
from pathlib import Path

# ─── Criteria Functions ──────────────────────────────────────────────────────────
def length_score(pw: str) -> int:
    return min(len(pw) // 4, 2)

def uppercase_score(pw: str) -> int:
    return 1 if re.search(r'[A-Z]', pw) else 0

def lowercase_score(pw: str) -> int:
    return 1 if re.search(r'[a-z]', pw) else 0

def digit_score(pw: str) -> int:
    return 1 if re.search(r'\d', pw) else 0

def special_score(pw: str) -> int:
    return 1 if re.search(r'\W', pw) else 0

def assess_password(pw: str) -> dict:
    scores = {
        'length'   : length_score(pw),
        'uppercase': uppercase_score(pw),
        'lowercase': lowercase_score(pw),
        'digits'   : digit_score(pw),
        'special'  : special_score(pw)
    }
    total = sum(scores.values())
    if total <= 2:
        verdict = 'Weak'
    elif total <= 4:
        verdict = 'Moderate'
    else:
        verdict = 'Strong'
    return {'scores': scores, 'total': total, 'verdict': verdict}

# ─── Main Entrypoint ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Password Strength Checker")
    parser.add_argument('--config', type=Path, help='JSON config file')
    parser.add_argument('--password', type=str, help='Password to assess')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

    pw = args.password
    if args.config:
        try:
            cfg = json.loads(Path(args.config).read_text())
            pw = cfg.get('password', pw)
        except Exception as e:
            logging.error(f"Failed loading config: {e}")
            sys.exit(1)

    if not pw:
        logging.error("No password provided; use --password or --config")
        sys.exit(1)

    result = assess_password(pw)
    print(f"Password Verdict: {result['verdict']}")
    print(f"Score Breakdown: {result['scores']} (Total: {result['total']})")

if __name__ == '__main__':
    main()
