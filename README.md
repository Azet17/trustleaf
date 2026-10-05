# TrustLeaf — Verifiable Supplier Trust Score

**An Intelligent Contract on GenLayer that computes on-chain trust scores for B2B suppliers from live web evidence and authoritative sanction lists — adjudicated by GenLayer's AI validator jury.**

> Submission for GenLayer Project Explorer · Built by Azet

---

## The Trust Problem

B2B supplier reputation today is controlled by **centralized platforms** (Alibaba, Global Sources, etc.):

- Scores can be **manipulated by the platform itself** — no independent verification
- "Verified supplier" badges are **outdated or purchasable**
- International buyers have **no independent way** to answer: *"Can I trust this supplier with a $50K wire transfer?"*

**Deterministic smart contracts cannot solve this.** Assessing whether a supplier's website constitutes trustworthy evidence requires *live web access* and *subjective judgment* — exactly what GenLayer's Intelligent Contracts are built for.

## What TrustLeaf Does

1. **Registers** a supplier (name, website, country) on-chain
2. **Fetches live evidence** during contract execution:
   - Renders the supplier's website in real time (`gl.nondet.web.render`)
   - Screens against **OFAC sanctions lists** (authoritative source)
3. **AI validator jury adjudicates** trust signals via the Equivalence Principle:
   - Is the site reachable?
   - Does it show real contact info?
   - Does it show genuine business identity (registration, legal form)?
   - Product/service clarity?
   - Sanctions hit → automatic zero
4. **Stores score + human-readable rationale on-chain** — auditable forever
5. **Appeal flow**: suppliers submit new evidence URLs → fresh live evaluation → score adjustment with on-chain rationale

## Why It's Impossible on Traditional Blockchains

| Capability | Ethereum/Solidity | GenLayer |
|---|---|---|
| Read live websites during execution | ❌ Oracles return fixed data | ✅ Native `gl.nondet.web` |
| Judge "is this evidence trustworthy?" | ❌ No subjective reasoning | ✅ AI validator jury + Equivalence Principle |
| Natural-language rationale on-chain | ❌ No | ✅ Stored in contract state |
| Appeal with arbitrary evidence URLs | ❌ Not possible | ✅ Fresh live evaluation per appeal |

## Contract API

| Method | Type | Description |
|---|---|---|
| `register_supplier(name, website, country)` | write | Register + immediate live scoring |
| `get_score(supplier_id)` | view | Full JSON: score, signals, rationale |
| `appeal_score(supplier_id, evidence_url)` | write | Appeal with new evidence → re-scored |
| `get_appeal(appeal_id)` | view | Appeal record + rationale |
| `is_sanctioned(supplier_id)` | view | Sanctions screen result |
| `total_suppliers()` | view | Registry size |

## Score Composition (0–100)

| Signal | Points | Source |
|---|---|---|
| Website reachable | 20 | Live render |
| Contact info present | 20 | Live render |
| Business identity signals | 25 | Live render |
| Product/service clarity | 25 | Live render |
| **Sanctions hit** | **auto-zero** | OFAC list |

## Real-World Path to Adoption

- **Procurement DAOs**: pre-trade supplier check before releasing escrowed funds
- **Agentic commerce** (Coinbase x402, ERC-8004 agent identity): autonomous agents query TrustLeaf as a trust oracle before transacting with unknown suppliers
- **Insurance/escrow**: smart policies priced on verified supplier scores

TrustLeaf exposes scores as on-chain state — any agent or contract can consume them permissionlessly.

## Project Structure

```
trustleaf/
├── contracts/
│   └── supplier_trust.py    # Intelligent Contract (Python)
├── frontend/                # React dApp — genuinely calls the contract
└── docs/
```

## Deployment

1. Open the **GenLayer Simulator** ([docs](https://docs.genlayer.com/developers/building-on-genlayer/setting-up/genlayer-simulator))
2. Create a new project → paste `contracts/supplier_trust.py`
3. Deploy → call `register_supplier("Acme Industrial", "https://acme.example", "Germany")`
4. Call `get_score(1)` → see live-computed score + rationale

## Team

Built by [Azet](https://portal.genlayer.foundation) — GenLayer builder.

## License

MIT
