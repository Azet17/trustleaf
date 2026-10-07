#!/bin/bash
# FINAL purge: FORM_FILL.md simulator block + drop cleanup.sh from repo
set -e
cd /home/ubuntu/trustleaf
git rm -q cleanup.sh 2>/dev/null || true
printf "cleanup.sh\n" >> .gitignore
python3 << 'PYEOF'
import re
p = 'docs/FORM_FILL.md'
src = open(p).read()
new_step = """1. Deploy via genlayer CLI to Testnet Bradbury (REAL network):
   genlayer network set testnetBradbury
   genlayer deploy --contract contracts/supplier_trust.py
   (or via studio.genlayer.com: paste contracts/supplier_trust.py, Deploy)"""
src = re.sub(
    r"1\. Open GenLayer Studio \(studio\.genlayer\.com\) or local Simulator\n.*?genlayer-simulator:latest\)",
    new_step, src, flags=re.S)
open(p, 'w').write(src)
print('FORM_FILL purged')
PYEOF
git add -A
git commit -qm "docs: final purge — zero simulator instructions"
git push origin main
echo "=== ABSOLUTE FINAL: any simulator mention outside fix-notes? ==="
git ls-files | xargs grep -niE "simulator" 2>/dev/null | grep -viE "no simulator|zero simulator" || echo "CLEAN — all remaining mentions are fix-notes only"
echo "=== tracked files ==="
git ls-files
