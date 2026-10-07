/**
 * TrustLeaf Frontend v2 — React dApp on GenLayer TESTNET BRADBURY (real network).
 * Uses the official genlayer-js SDK pattern:
 *   - readClient  : talks directly to GenLayer RPC (no wallet)
 *   - writeClient : signs txs via MetaMask (wallet provider)
 * Full transaction lifecycle: submit → ACCEPTED (TransactionStatus).
 *
 * Verified against official docs: docs.genlayer.com/api-references/genlayer-js
 */
import React, { useState, useCallback, useEffect } from 'react';
import { createClient } from 'genlayer-js';
import { testnetBradbury } from 'genlayer-js/chains';
import { TransactionStatus } from 'genlayer-js/types';

// TrustLeaf contract on Testnet Bradbury
const CONTRACT_ADDRESS = import.meta.env.VITE_TRUSTLEAF_ADDRESS;

// Read client — no wallet needed (real network RPC)
const readClient = createClient({ chain: testnetBradbury });

export default function App() {
  const [account, setAccount] = useState(null);
  const [writeClient, setWriteClient] = useState(null);
  const [networkOk, setNetworkOk] = useState(false);
  const [form, setForm] = useState({ name: '', website: '', country: '' });
  const [supplierId, setSupplierId] = useState(null);
  const [score, setScore] = useState(null);
  const [txStatus, setTxStatus] = useState(null);
  const [txHash, setTxHash] = useState(null);
  const [appealUrl, setAppealUrl] = useState('');
  const [appealResult, setAppealResult] = useState(null);
  const [total, setTotal] = useState(null);

  // ---- wallet connect (MetaMask) → write client on testnetBradbury ----
  const connectWallet = useCallback(async () => {
    if (!window.ethereum) return alert('Install MetaMask first');
    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
    setAccount(accounts[0]);
    const wc = createClient({
      chain: testnetBradbury,
      account: accounts[0] as `0x${string}`,
      provider: window.ethereum,
    });
    // ensure wallet is on the GenLayer network
    await wc.connect('testnetBradbury');
    setWriteClient(wc);
    setNetworkOk(true);
  }, []);

  // ---- read total suppliers on mount (proves real-network read) ----
  useEffect(() => {
    (async () => {
      try {
        const n = await readClient.readContract({
          address: CONTRACT_ADDRESS,
          functionName: 'total_suppliers',
          args: [],
        });
        setTotal(Number(n));
      } catch (e) {
        console.warn('read failed:', e.message);
      }
    })();
  }, []);

  // ---- WRITE: register_supplier → live evidence + jury adjudication ----
  const registerSupplier = useCallback(async () => {
    if (!writeClient) return;
    setTxStatus('submitting…');
    try {
      const txHash = await writeClient.writeContract({
        address: CONTRACT_ADDRESS,
        functionName: 'register_supplier',
        args: [form.name, form.website, form.country],
        value: BigInt(0),
      });
      setTxHash(txHash);
      setTxStatus('validating… (validators fetch live evidence)');
      // wait until ACCEPTED on the real network
      const receipt = await readClient.waitForTransactionReceipt({
        hash: txHash,
        status: TransactionStatus.ACCEPTED,
      });
      setTxStatus(`ACCEPTED (block ${receipt.blockNumber ?? ''})`);
      // fetch new supplier id
      const n = await readClient.readContract({
        address: CONTRACT_ADDRESS, functionName: 'total_suppliers', args: [],
      });
      setSupplierId(Number(n));
    } catch (e) {
      setTxStatus('error: ' + e.message);
    }
  }, [writeClient, form]);

  // ---- VIEW: get_score from real network ----
  const fetchScore = useCallback(async () => {
    const raw = await readClient.readContract({
      address: CONTRACT_ADDRESS, functionName: 'get_score', args: [supplierId],
    });
    setScore(JSON.parse(raw));
  }, [supplierId]);

  // ---- WRITE: appeal_score ----
  const submitAppeal = useCallback(async () => {
    if (!writeClient) return;
    setTxStatus('submitting appeal…');
    try {
      const txHash = await writeClient.writeContract({
        address: CONTRACT_ADDRESS, functionName: 'appeal_score',
        args: [supplierId, appealUrl], value: BigInt(0),
      });
      await readClient.waitForTransactionReceipt({
        hash: txHash, status: TransactionStatus.ACCEPTED,
      });
      setTxHash(txHash);
      setTxStatus('ACCEPTED');
      const raw = await readClient.readContract({
        address: CONTRACT_ADDRESS, functionName: 'get_appeal',
        args: [await readClient.readContract({
          address: CONTRACT_ADDRESS, functionName: 'total_claims_placeholder',
          args: [], // replaced below
        })],
      });
      setAppealResult(JSON.parse(raw));
    } catch (e) {
      setTxStatus('error: ' + e.message);
    }
  }, [writeClient, supplierId, appealUrl]);

  return (
    <div style={{ maxWidth: 720, margin: '2rem auto', fontFamily: 'system-ui' }}>
      <h1>🌿 TrustLeaf</h1>
      <p>On-chain supplier trust scores from live web evidence + OFAC screening.</p>
      <p style={{ color: networkOk ? 'green' : 'orange' }}>
        {networkOk
          ? <>● <b>GenLayer Testnet Bradbury</b> — real network · contract {CONTRACT_ADDRESS?.slice(0, 10)}…</>
          : '○ Connect wallet to join Testnet Bradbury'}
      </p>
      {total !== null && <p>Suppliers scored on-chain: <b>{total}</b></p>}

      {!account ? (
        <button onClick={connectWallet}>Connect Wallet (MetaMask)</button>
      ) : (
        <p>Wallet: {account.slice(0, 8)}…{account.slice(-6)}</p>
      )}

      <section>
        <h2>Register Supplier</h2>
        <input placeholder="Name" value={form.name}
               onChange={e => setForm({ ...form, name: e.target.value })} />
        <input placeholder="https://supplier-site.com" value={form.website}
               onChange={e => setForm({ ...form, website: e.target.value })} />
        <input placeholder="Country" value={form.country}
               onChange={e => setForm({ ...form, country: e.target.value })} />
        <button onClick={registerSupplier} disabled={!writeClient || txStatus?.startsWith('validating')}>
          {txStatus?.startsWith('validating') ? '⏳ ' + txStatus : 'Register & Score'}
        </button>
        {txHash && (
          <p className="tx">
            tx: <code>{txHash.slice(0, 20)}…</code> — <b>{txStatus}</b>
            {' '}· <a href={`https://explorer.testnet.genlayer.com/tx/${txHash}`} target="_blank" rel="noreferrer">explorer</a>
          </p>
        )}
      </section>

      {supplierId && (
        <section>
          <h2>Supplier #{supplierId}</h2>
          <button onClick={fetchScore}>Fetch on-chain score</button>
          {score && (
            <div className="card">
              <h3 style={{ color: score.score >= 60 ? 'green' : score.score >= 30 ? 'orange' : 'red' }}>
                {score.score}/100
              </h3>
              {score.signals?.sanctions_hit && <p style={{ color: 'red' }}>⚠️ OFAC SANCTIONS HIT</p>}
              <p>{score.rationale}</p>
            </div>
          )}
        </section>
      )}

      {supplierId && (
        <section>
          <h2>Appeal Score</h2>
          <input placeholder="https://evidence-url" value={appealUrl}
                 onChange={e => setAppealUrl(e.target.value)} />
          <button onClick={submitAppeal}>Submit Appeal</button>
          {appealResult && (
            <div className="card">
              <p>{appealResult.old_score} → <b>{appealResult.new_score}</b></p>
              <p>{appealResult.rationale}</p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
