#!/usr/bin/env python3
import re
import sys
import urllib.request
from datetime import datetime, timezone
import os

SRC_URL = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Shadowrocket/ChinaMax/ChinaMax_Domain.list"
OUT_PATH = "output/alidns_chinamax_host.module"
DNS = "https://dns.alidns.com/dns-query"

def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def main():
    text = fetch(SRC_URL)

    lines_out = []
    seen = set()

    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#") or s.startswith("//"):
            continue

        s = s.split("#", 1)[0].strip()
        s = s.split("//", 1)[0].strip()
        if not s:
            continue

        if s.startswith("."):
            host = "*" + s   # ".abc.com" -> "*.abc.com"
        else:
            host = s

        if not re.fullmatch(r"(\*\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}", host):
            continue

        line = f"{host} = server:{DNS}"
        if line not in seen:
            seen.add(line)
            lines_out.append(line)

    lines_out.sort()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    os.makedirs("output", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("#!name=AliDNS for ChinaMax Domains\n")
        f.write("#!desc=Auto-generated. Domains in ChinaMax_Domain.list resolve via AliDNS DoH.\n")
        f.write(f"#!updated={now}\n\n")
        f.write("[Host]\n")
        f.write("\n".join(lines_out))
        f.write("\n")

    print(f"wrote {OUT_PATH} lines={len(lines_out)}")

if __name__ == "__main__":
    sys.exit(main())
