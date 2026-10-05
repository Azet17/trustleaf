# TrustLeaf — FORM FILL (copy-paste untuk portal.genlayer.foundation)

## STEP 1 — IDENTITY
Project Name : TrustLeaf
Logo         : (upload trustleaf_logo.png — hijau, leaf + shield)
Primary Tag  : Oracle   (alternatif: DeFi / AI — pilih yang ada di dropdown)
Tag 1        : Reputation
Tag 2        : Verification

## STEP 2 — ONE-LINER
"An on-chain oracle that scores B2B supplier trust from live web
evidence and OFAC sanction screening, adjudicated by GenLayer's
AI validator jury."

## STEP 3 — DESCRIPTION
TrustLeaf solves a trust problem deterministic smart contracts
cannot touch: vendor reputation in B2B procurement is controlled
by centralized platforms (Alibaba-style scores) that can be
manipulated, bought, or left stale. International buyers have no
independent way to verify "can I trust this supplier with a
$50K transfer?" before releasing funds.

TrustLeaf registers suppliers on-chain and computes a 0-100
trust score by fetching LIVE evidence during contract execution:
the supplier's website is rendered in real time
(gl.nondet.web.render) and screened against authoritative OFAC
sanction lists. Trust signals — site reachability, contact info,
business identity, product clarity — are judged subjectively by
GenLayer's AI validator jury through the Equivalence Principle.
Score plus a human-readable rationale is stored on-chain,
auditable forever. Suppliers can appeal with new evidence URLs,
triggering fresh live re-evaluation with on-chain rationale for
every adjustment.

Why this is impossible on Ethereum: reading live websites during
execution, subjective judgment of evidence quality, and
natural-language rationale all require GenLayer's AI-native
adjudication layer. The score lives as on-chain state, so
procurement DAOs, escrow contracts, and autonomous agents
(x402 / ERC-8004 commerce) can consume TrustLeaf
permissionlessly as a pre-trade trust check.

Differentiation from existing GenLayer projects (FUD Markets,
BuildersClaw, AutoBounty, Mandate Court, CiteFlow): no existing
project combines authoritative sanction-list screening, live web
evidence, an appeal loop, and score history into a reusable
trust primitive for agentic commerce.

## STEP 4 — SHOW IT IN ACTION (YouTube demo URL)
TODO: record 3-5 min demo:
1. Show contract in Studio (code visible)
2. Deploy to testnet, register real supplier site
3. Show "validators adjudicating" tx lifecycle + explorer tx
4. Fetch score → rationale rendered on-chain
5. Register sanctions-name supplier → auto-zero
6. Appeal flow → score adjustment
(Upload unlisted → paste URL)

## STEP 5 — WRITE THE EXACT PATH (how to reproduce)
1. Open GenLayer Studio (studio.genlayer.com) or local Simulator
   (docker run -d -p 8484:8484 ghcr.io/yeagerai/genlayer-simulator:latest)
2. New project → paste contracts/supplier_trust.py from repo
3. Deploy → note contract address
4. Call register_supplier("Acme Industrial",
   "https://acme-industrial.com", "Germany")
5. Wait ~1-2 min (validator consensus on live evidence)
6. Call get_score(1) → JSON with score, signals, rationale
7. Frontend: cd frontend && npm install && npm run dev
   (set VITE_TRUSTLEAF_ADDRESS=<address> in .env)
8. Connect MetaMask → register → watch tx lifecycle → fetch score

## STEP 6 — PROVE THE PATH WORKS (visible to stewards)
"After deploying contracts/supplier_trust.py and calling
register_supplier with a real business website, get_score returns
a 0-100 score with a natural-language rationale (e.g. 'site
reachable; contact info present; business identity signals
present; sanctions screen: clear. Computed trust score: 90/100').
Registering a sanctioned entity returns score 0 with 'OFAC
SANCTIONS HIT'. The frontend renders every value from on-chain
state via genuine read/write calls, with tx hashes verifiable in
the explorer. Appeal with a certificate URL re-scores live."

## STEP 7 — CONTRACT LINKS
Studio URL  : (paste after deploying in studio.genlayer.com)
Explorer URL: (paste testnet explorer tx/deployment link)

## STEP 8 — PROJECT LINKS (required)
Website : https://github.com/Azet17/trustleaf  (atau GitHub Pages
          setelah deploy frontend: https://azet17.github.io/trustleaf/)
GitHub  : https://github.com/Azet17/trustleaf

## STEP 9 — EVIDENCE
GitHub Repository URL : https://github.com/Azet17/trustleaf
(opsional tambah: YouTube demo URL, X post thread)
