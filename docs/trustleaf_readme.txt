# TrustLeaf — Verifiable Supplier Trust Score

**An Intelligent Contract on GenLayer that computes on-chain trust scores for B2B suppliers from live web evidence and authoritative OFAC sanction lists — adjudicated by GenLayer's AI validator jury.**

> GenLayer Project Explorer submission · v2 (addresses prior review feedback)

---

## What's New in v2

- **Real network, no simulator**: frontend built on the official `genlayer-js` SDK with `createClient({ chain: testnetBradbury })` — a read client (direct RPC) and a MetaMask-signed write client on **Testnet Bradbury**. Zero simulator dependencies.
- **GenVM-compliant storage**: state uses only supported persistent types — `TreeMap[str, str]` collections and `bigint` counters (no `dict`/`int`).
- **Deployed on-chain**: contract live at `0x6ce3f249368ce5B28E9906ffA3a3Be1eF1b08b32`, deploy tx ACCEPTED.

## The Trust Problem

B2B supplier reputation is controlled by centralized platforms (Alibaba-style scores) that can be manipulated, purchased, or left stale. International buyers have no independent way to answer: *"can I trust this supplier with a $50K wire transfer?"*

Deterministic smart contracts cannot solve this — assessing whether a supplier's website constitutes trustworthy evidence requires **live web access** and **subjective judgment**, exactly what GenLayer Intelligent Contracts provide.

## How It Works

1. **Register** a supplier (name, website, country) on-chain
2. **Live evidence**: the supplier's website is rendered during execution (`gl.nondet.web.render`) and screened against **OFAC sanctions lists** (authoritative source)
3. **AI validator jury** adjudicates trust signals via `gl.eq_principle.strict_eq` — site reachable? contact info present? genuine business identity? product clarity? sanctions hit → automatic zero
4. **Score 0–100 + human-readable rationale** stored on-chain
5. **Appeal flow**: suppliers submit new evidence URLs → fresh live re-evaluation with on-chain rationale

## Contract API

| Method | Type | Description |
|---|---|---|
| `register_supplier(name, website, country)` | write | Register + immediate live scoring |
| `get_score(supplier_id)` | view | JSON: score, signals, rationale |
| `appeal_score(supplier_id, evidence_url)` | write | Appeal → fresh live re-score |
| `is_sanctioned(supplier_id)` | view | OFAC screen result |
| `total_suppliers()` | view | Registry size |

## Storage (GenVM-compliant)

```python
class SupplierTrustScore(gl.Contract):
    supplier_counter: bigint
    suppliers: TreeMap[str, str]   # id -> JSON verdict record
    appeals: TreeMap[str, str]
    appeal_counter: bigint
```

No `dict`, no `int` — only GenLayer-supported persistent storage types.

## Frontend (real network)

The React dApp connects to **Testnet Bradbury** via the official SDK:

```typescript
import { createClient } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { TransactionStatus } from 'genlayer-js/types';

const readClient = createClient({ chain: testnetBradbury });       // RPC, no wallet
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

Full component: [`frontend/App.jsx`](frontend/App.jsx)

## Why Impossible on Deterministic Chains

- Reading live websites **during execution** — no oracle round-trips
- Subjective judgment of evidence quality — validator jury + Equivalence Principle
- Natural-language rationale stored on-chain
- Open appeal flow with fresh live evaluation per appeal

## Real Use Cases

- **Procurement DAOs**: pre-trade supplier check before releasing escrow
- **Agentic commerce** (x402 / ERC-8004): autonomous agents query TrustLeaf as a trust oracle before transacting with unknown suppliers
- **Insurance/escrow**: policies priced on verified supplier scores

## Repository Layout

```
trustleaf/
├── contracts/supplier_trust.py   # Intelligent Contract (GenVM-compliant storage)
├── frontend/App.jsx              # React dApp — testnetBradbury real network
├── docs/DEPLOY.md                # Deployment guide (CLI + frontend)
└── README.md
```

## License

MIT
