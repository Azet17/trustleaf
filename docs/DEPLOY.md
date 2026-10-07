# TrustLeaf — Deployment Guide (v2 — Testnet Bradbury)

## Contract (already deployed — reuse or redeploy)

**Contract address (Studio testnet deploy):**
`0x6ce3f249368ce5B28E9906ffA3a3Be1eF1b08b32`
**Deploy tx:** `0x114ce1ad298639d5eb9621dd9294994d594d73b22551c37cefbe02ad6ddf2617` (ACCEPTED)

### Redeploy to Testnet Bradbury via genlayer CLI (real network):

```bash
npm install -g @genlayer/cli   # or: uv tool install genlayer
genlayer network set testnetBradbury
genlayer deploy --contract contracts/supplier_trust.py
# → returns REAL testnet contract address; put it in frontend/.env
```

## Frontend (v2 — real network via genlayer-js)

```bash
cd frontend
npm create vite@latest . -- --template react
npm install genlayer-js
echo "VITE_TRUSTLEAF_ADDRESS=0x<your-testnet-address>" > .env
# replace src/App.jsx with this repo's App.jsx
npm run dev
```

**What changed in v2 (steward feedback addressed):**
- ❌ OLD: `SimulatorTransport` (local simulator only)
- ✅ NEW: `createClient({ chain: testnetBradbury })` — REAL GenLayer network
- ✅ readClient (RPC direct) + writeClient (MetaMask-signed) per official SDK pattern
- ✅ `waitForTransactionReceipt({ status: TransactionStatus.ACCEPTED })` — real consensus wait
- ✅ `client.connect('testnetBradbury')` — wallet auto-switches network

## Steward verification script

1. Open the deployed frontend URL
2. Banner shows: **"● GenLayer Testnet Bradbury — real network"**
3. "Suppliers scored on-chain: N" — live read from the real testnet
4. Connect MetaMask → auto-switches to GenLayer Bradbury network
5. Register a supplier → tx hash → wait ACCEPTED on real network
6. `get_score` returns on-chain JSON with rationale
