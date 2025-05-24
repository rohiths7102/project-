#!/usr/bin/env python3






import argparse
import json
import logging
import sys
from pathlib import Path

# ─── Core Cipher ────────────────────────────────────────────────────────────────
def caesar(text: str, shift: int, decrypt: bool = False) -> str:
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            idx = (ord(ch) - base + (-shift if decrypt else shift)) % 26
            result.append(chr(base + idx))
        else:
            result.append(ch)
    return ''.join(result)

def main():
    parser = argparse.ArgumentParser(description="Caesar Cipher CLI Tool")
    parser.add_argument('--config', type=Path, help='JSON config file')
    parser.add_argument('--text', type=str, help='Message text')
    parser.add_argument('--shift', type=int, help='Shift value (0–25)')
    parser.add_argument('--mode', choices=['encrypt','decrypt'], help='Operation mode')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

    cfg = {}
    if args.config:
        try:
            cfg = json.loads(args.config.read_text())
        except Exception as e:
            logging.error(f"Config error: {e}")
            sys.exit(1)

    text = cfg.get('text', args.text)
    shift = cfg.get('shift', args.shift)
    mode  = cfg.get('mode', args.mode)

    if text is None or shift is None or mode is None:
        logging.error("Missing required: --text, --shift, --mode (or via config)")
        sys.exit(1)

    decrypt = (mode == 'decrypt')
    out = caesar(text, shift, decrypt)
    print(f"Result ({mode}): {out}")

if __name__ == '__main__':
    main()
