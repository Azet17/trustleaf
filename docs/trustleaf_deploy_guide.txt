# Deploy TrustLeaf — Testnet Bradbury (Real Network)

## 1. Deploy the Contract

**Option A — genlayer CLI (real testnet):**
```bash
npm install -g @genlayer/cli   # or: uv tool install genlayer
genlayer network set testnetBradbury
genlayer network info           # verify network
genlayer deploy --contract contracts/supplier_trust.py
# → returns testnet contract address; put it in frontend/.env as VITE_TRUSTLEAF_ADDRESS
```

**Option B — GenLayer Studio:** open studio.genlayer.com → new project → paste `contracts/supplier_trust.py` → Deploy (studio uses studionet; for Bradbury use the CLI).

**Reference deployment (Studio testnet):** `0x6ce3f249368ce5B28E9906ffA3a3Be1eF1b08b32` — tx `0x114ce1ad298639d5eb9621dd9294994d594d73b22551c37cefbe02ad6ddf2617` ACCEPTED.

## 2. Run the Frontend (Testnet Bradbury — real network)

```bash
cd frontend
npm create vite@latest . -- --template react
npm install genlayer-js
echo "VITE_TRUSTLEAF_ADDRESS=0x<testnet-address>" > .env
# replace src/App.jsx with this repo's App.jsx
npm run dev
```

**v2 network config (no simulator):**
```typescript
import { createClient } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { TransactionStatus } from 'genlayer-js/types';

const readClient = createClient({ chain: testnetBradbury });       // direct RPC
const writeClient = createClient({                                  // MetaMask-signed
  chain: testnetBradbury,
  account: address as `0x${string}`,
  provider: window.ethereum,
});
await writeClient.connect('testnetBradbury');                       // auto network switch
const receipt = await readClient.waitForTransactionReceipt({
  hash: txHash, status: TransactionStatus.ACCEPTED,
});
```

## 3. Steward verification script

1. Open the frontend → banner: **"● GenLayer Testnet Bradbury — real network"**
2. "Suppliers scored on-chain: N" — live read from real testnet (no simulator)
3. Connect MetaMask → wallet auto-switches to GenLayer Bradbury network
4. Register supplier → tx hash → `waitForTransactionReceipt(status: ACCEPTED)` on real network
5. `get_score` → on-chain JSON with rationale
6. OFAC-sanctioned supplier → auto-zero
7. Appeal → fresh live re-evaluation

## Storage compliance (GenVM)

`TreeMap[str, str]` collections + `bigint` counters only — no `dict`/`int` class attributes (unsupported by GenVM persistent storage).
