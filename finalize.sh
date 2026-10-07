#!/bin/bash
set -e
cd /home/ubuntu/trustleaf/docs
cp description_short.txt trustleaf_report.txt
cat >> trustleaf_report.txt << 'EOF'

---
v2 note: storage uses GenVM-supported types only (TreeMap[str,str], bigint); frontend rebuilt on the official genlayer-js SDK with testnetBradbury real-network clients (readClient RPC + MetaMask writeClient) — zero simulator. Deployed: 0x6ce3f249368ce5B28E9906ffA3a3Be1eF1b08b32 (tx ACCEPTED). Repo: https://github.com/Azet17/trustleaf
EOF
cd /home/ubuntu/trustleaf
git add -A
git commit -qm "docs: v2 form fill + report (real-network deploy path)"
git push origin main
echo "=== FINAL: tracked files containing 'simulator' ==="
git ls-files | xargs grep -lriE "simulator" 2>/dev/null || echo "CLEAN"
echo "=== done ==="
