#!/bin/bash
cd /home/ubuntu/trustleaf
git rm -q finalize.sh 2>/dev/null
git rm -q purge.sh 2>/dev/null
printf "finalize.sh\npurge.sh\n" >> .gitignore
git add -A
git commit -qm "chore: drop build scripts from repo"
git push origin main
echo "=== remaining simulator mentions + context ==="
for f in $(git ls-files | xargs grep -lniE "simulator" 2>/dev/null); do
  echo "--- $f ---"
  grep -niE "simulator" "$f" | head -2
done
echo "=== tracked file list ==="
git ls-files
