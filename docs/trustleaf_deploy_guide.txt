# TrustLeaf — Deployment & Review Guide (for stewards)

## 1. Deploy the Intelligent Contract (5 minutes)

**Via GenLayer Simulator:**
```bash
# Install simulator per official docs:
# https://docs.genlayer.com/developers/building-on-genlayer/setting-up/genlayer-simulator
docker run -d -p 8484:8484 --name genlayer-simulator ghcr.io/yeagerai/genlayer-simulator:latest
# Open http://localhost:8484 → Studio → New Project
# Paste contracts/supplier_trust.py → Deploy
# Note the contract address
```

**Via Testnet Bradbury:** use GenLayer Studio (studio.genlayer.com) → new project → paste contract → deploy → copy address.

## 2. Run the Frontend

```bash
cd frontend
npm create vite@latest . -- --template react
npm install genlayer-js
echo "VITE_TRUSTLEAF_ADDRESS=<your_contract_address>" > .env
# Replace src/App.jsx with this repo's App.jsx
npm run dev
# Open http://localhost:5173
```

## 3. What the steward will see (verification script)

1. **Connect Wallet** — MetaMask popup, address shown
2. **Register Supplier** with `name=Acme GmbH, website=https://acme-real-site.com, country=Germany`
   - Button shows *"Validators adjudicating live evidence…"* (tx lifecycle: pending → validated → finalized)
   - tx hash displayed with explorer link
3. **Fetch on-chain score** → 0–100 score + human-readable rationale rendered FROM CONTRACT STATE (not mock)
4. Register a supplier with a sanctions-list name → score auto-zero with "OFAC SANCTIONS HIT" banner
5. **Appeal** with a certificate URL → score adjusted live, both old/new scores + rationale shown

Every UI state comes from a real contract call — no hardcoded data.

## 4. Contract deployment links

Deploy once on Testnet Bradbury and paste the explorer URL into the submission form (Studio / explorer URLs are accepted by the portal).
