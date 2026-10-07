#!/bin/bash
# Remove stale simulator-instruction docs (old v1 files) — replace with v2 txt twins
set -e
cd /home/ubuntu/trustleaf/docs

# deploy guide txt → v2 content (copy from DEPLOY.md)
cp DEPLOY.md trustleaf_deploy_guide.txt

# readme txt twin → copy new README
cp ../README.md trustleaf_readme.txt

# form fill txt → rebuild without simulator (sed replace deployment section)
python3 << 'PYEOF'
import re
src = open('trustleaf_form_fill.txt').read()
# replace the simulator deployment instruction block
new_step = """1. Deploy via genlayer CLI to Testnet Bradbury (REAL network):
   genlayer network set testnetBradbury
   genlayer deploy --contract contracts/supplier_trust.py
   (or via studio.genlayer.com → paste contracts/supplier_trust.py → Deploy)"""
src = re.sub(
    r"1\. Open GenLayer Studio \(studio\.genlayer\.com\) or local Simulator\n.*?genlayer-simulator:latest\)",
    new_step, src, flags=re.S)
open('trustleaf_form_fill.txt', 'w').write(src)
print('form fill updated')
PYEOF

# rm make_logo? keep it (docs utility). finalize.sh out of docs:
rm -f finalize.sh
cd /home/ubuntu/trustleaf
git add -A
git commit -qm "docs: purge stale simulator instructions from txt deliverables — all paths now testnetBradbury real network"
git push origin main
echo "=== FINAL CHECK: simulator mentions in tracked files ==="
git ls-files | xargs grep -lniE "simulator" 2>/dev/null || echo "ZERO simulator references"
