#!/usr/bin/env python3






import argparse
import json
import logging
import sys
from pathlib import Path

from scapy.all import sniff, conf  # 

def packet_handler(pkt):
    try:
        layer = pkt.payload
        src = pkt.src
        dst = pkt.dst
        proto = pkt.proto if hasattr(pkt, 'proto') else layer.name
        logging.info(f"{src} -> {dst} | {proto}")
        print(f"{src} -> {dst} | {proto}")
    except Exception as e:
        logging.error(f"Error processing packet: {e}")

def main():
    parser = argparse.ArgumentParser(description="Custom Packet Sniffer")
    parser.add_argument('--config', type=Path, help='JSON config file')
    parser.add_argument('--iface', type=str, help='Interface to sniff on')
    parser.add_argument('--filter', type=str, default='ip', help='BPF filter string')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    lvl = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=lvl,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        handlers=[logging.StreamHandler(),
                                  logging.FileHandler('sniffer.log', encoding='utf-8')])

    cfg = {}
    if args.config:
        try:
            cfg = json.loads(args.config.read_text())
        except Exception as e:
            logging.error(f"Config parse error: {e}")
            sys.exit(1)

    iface = cfg.get('iface', args.iface)
    fltr  = cfg.get('filter', args.filter)

    if not iface:
        logging.error("Interface not specified (--iface or in config)")
        sys.exit(1)

    logging.info(f"Starting sniff on {iface} with filter '{fltr}'")
    try:
        sniff(iface=iface, filter=fltr, prn=packet_handler)
    except Exception as e:
        logging.error(f"Sniffing failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
