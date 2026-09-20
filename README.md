# 🛡️ MuleGuard
### *Explainable UPI Fraud & Coordinated Mule-Network Intelligence*
**Tagline:** *"Detect the network. Explain the risk. Protect the transaction."*  
**Built for:** **MEGATHON'26 – Fusion For Future**

---

## 📌 Overview
**MuleGuard** is an explainable UPI fraud-detection prototype that identifies suspicious mule-account networks instead of analyzing transactions solely in isolation. 

While traditional transaction-by-transaction fraud filters often miss money-muling operations that split or rapidly route illicit funds, MuleGuard combines **Scikit-Learn behavioral anomaly scoring** with **NetworkX topological graph mining** to detect coordinated multi-account syndicates in real time.

---

## 🛑 Problem
UPI fraud increasingly involves organized, distributed networks of **mule accounts** that receive and rapidly forward money through multi-hop accounts:
- **Fan-In Aggregation:** Multiple victims or source accounts funnel funds into a single collector mule within minutes.
- **Fan-Out Smurfing:** A mule account immediately disperses pooled funds across multiple recipient accounts to stay under single-transaction reporting thresholds.
- **Rapid Fund Forwarding (Pass-Through):** Accounts hold money for mere minutes, forwarding 80–95% onward before victims realize they have been scammed.
- **Multi-Hop Layering Chains:** Funds traverse 3 to 5 intermediary hops to evade traditional point-in-time KYC and AML controls.

Traditional rule engines evaluating single transactions in isolation fail to detect these interconnected patterns.

---

## 💡 Solution
MuleGuard analyzes both:
1. **Individual Transaction Risk:** Transaction amount deviations, temporal velocity, counterparty frequency, and jurisdictional risk.
2. **Account Relationship Topologies:** Directed multigraph analytics that uncover structural anomalies (fan-in, fan-out, pass-through nodes, and directed acyclic layering paths).

### Core User Flow
```
Synthetic UPI Transactions
          ↓
  Feature Engineering
          ↓
Transaction Risk Scoring (Scikit-Learn)
          ↓
Transaction Network Construction (NetworkX)
          ↓
Mule Pattern Detection (Fan-In, Fan-Out, Rapid Forwarding, Multi-Hop Chains)
          ↓
Risk Explanation (Plain-English Diagnostics)
          ↓
   ALLOW / WARN / BLOCK
          ↓
Fraud Analyst Workstation & Customer Pre-Transfer Shield
```

---

## ✨ Key Features

- **⚡ 2-Minute Demo Scenario Mode:** One-click launcher designed specifically for hackathon judging, highlighting an active multi-tier syndicate with graph visualization and blocking recommendations.
- **🕸️ Graph Intelligence Engine:** Built on NetworkX, automatically uncovering:
  - *Fan-In:* High in-degree counterparty pooling within tight time windows.
  - *Fan-Out:* High out-degree rapid disbursement.
  - *Rapid Forwarding:* Inflow followed by immediate outbound forwarding (>70% volume within <45 minutes).
  - *Multi-Hop Chains:* Chronologically verified directed transfer sequences across accounts.
- **🎯 Transparent Demo Network Risk Score (0–100):** Clear, interpretable risk index categorized into:
  - `0–39`: **LOW ➔ ALLOW**
  - `40–69`: **MEDIUM ➔ WARN**
  - `70–100`: **HIGH ➔ BLOCK**
- **💡 Plain-Language Explainable AI (`generate_explanation()`):** Replaces opaque ML feature names with human-readable rationale (e.g., *"Received funds from 4 unrelated accounts within 35 minutes"*, *"Forwarded 94% of inbound funds within 6 minutes"*).
- **⚠️ Pre-Transfer Customer Protection Shield:** Simulated UPI mobile interface demonstrating explainable friction and warnings before a payment is confirmed.
- **🚨 Fraud Analyst Workstation & Feedback Audit:** Live alert queue with interactive investigation tools and persistent human-in-the-loop audit logging saved to `data/feedback.csv`.
- **🧪 Live Transaction Simulator:** Interactive test bench to inject custom UPI transactions and observe real-time graph recalculations and risk decisions.
- **🎨 Modern Dark Cybersecurity UI:** Built with custom glassmorphism panels, neon status badges (`● SYSTEM ONLINE`), and interactive Plotly graph visualizations.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MuleGuard Architecture                   │
└─────────────────────────────────────────────────────────────┘
                              │
               [ Synthetic UPI Transactions ]
                              │
               [ Feature Engineering Module ]
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
   [ Scikit-Learn Model ]            [ NetworkX Graph Engine ]
   • Temporal Velocity               • Directed Multigraph
   • Counterparty Frequency          • Fan-In / Fan-Out Mining
   • Amount Outliers                 • Multi-Hop Chain Tracing
             │                                 │
             └────────────────┬────────────────┘
                              ▼
                 [ Composite Decision Engine ]
                 • 0–39:  ALLOW (Green)
                 • 40–69: WARN  (Amber)
                 • 70–100: BLOCK (Crimson)
                              │
                              ▼
                [ Explainability Layer (XAI) ]
                • Plain-English Diagnostics
                • Transparent Factor Impact
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
[ Consumer Pre-Transfer Shield ]    [ Fraud Analyst Workstation ]
(Interactive Warning Screen)        (Alert Queue + Feedback Audit)
```

---

## 🛠️ Technology Stack

- **UI / Frontend:** [Streamlit](https://streamlit.io/) with custom dark fintech CSS theme.
- **Backend / Pipeline:** Python 3.10+
- **Data Engineering:** Pandas & NumPy
- **Machine Learning:** Scikit-Learn (Random Forest / Calibrated Classifier)
- **Graph Analytics:** NetworkX (Directed Graph Topology & Path Tracing)
- **Visualizations:** Plotly Graph Objects & Express
- **Storage:** CSV / Local Datasets (`data/transactions.csv`, `data/feedback.csv`)

---

## 🚀 Installation

1. **Clone or navigate to the repository:**
   ```bash
   cd MuleGuard
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Running the Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```
Or via Python module:
```bash
python -m streamlit run app.py
```
Open your browser at: `http://localhost:8501`

---

## 🎬 2-Minute Judging Demo Walkthrough

1. **Launch the app** and look at the sidebar.
2. Click **⚡ "Load 2-Minute Demo Scenario"**.
3. Observe:
   - Dashboard instantly navigates to **🕸️ Network Intelligence**.
   - The interactive graph visualizes syndicate **MG-NET-DEMO** (Victims funneled into `MULE_CORE_01`, layered through `MULE_LAYER_02`, and dispersed to exit gateways).
   - The pattern cards display verified **Fan-In**, **Rapid Forwarding**, and **Multi-Hop Chains**.
   - The account inspector shows a **Demo Network Risk Score of 94/100 (HIGH ➔ BLOCK)** with plain-language bullets.
4. Navigate to **🚨 Fraud Analyst Alerts**:
   - Review Alert `MG-NET-DEMO`.
   - Click **🚨 Confirm Fraud & Block Syndicate** and check the live audit trail saved to `data/feedback.csv`.
5. Navigate to **⚠️ Pre-Transfer Warning**:
   - View how a simulated consumer is protected from paying mule accounts.
6. Navigate to **🧪 Live Transaction Simulator**:
   - Enter a test transaction to an existing mule account (e.g. `M001`), click **⚡ Run Live MuleGuard Evaluation**, and see the immediate ALLOW/WARN/BLOCK decision.

---

## 📊 Synthetic Dataset

The prototype includes a deterministic synthetic dataset in `data/transactions.csv` containing:
- **Normal Transactions:** Genuine P2P and P2M transactions (e.g., `A001` ➔ `B001`, grocery and cafe payments).
- **Fan-In Topologies:** `A101`, `A102`, `A103`, `A104` ➔ `M001` (pooling ₹19,000).
- **Fan-Out Topologies:** `M001` ➔ `B201`, `B202`, `B203` (disbursing funds within 30 minutes).
- **Multi-Hop Layering:** `A105` ➔ `M002` ➔ `M003` ➔ `M004` ➔ `B204` (sequenced transfers).
- **Rapid Pass-Through:** `A106` ➔ `M005` (₹10,000) ➔ `M006` (₹9,500 within 6 minutes).
- **Syndicate Demo Ring (`MG-NET-DEMO`):** Victims ➔ `MULE_CORE_01` ➔ `MULE_LAYER_02` ➔ Offshore exit gateways.

---

## 🔒 Demo Safety & Disclaimer

> [!NOTE]
> **Prototype & Simulation Notice:**
> - **Synthetic transaction data only:** No real customer information, live bank credentials, or actual UPI accounts are accessed or stored.
> - **Simulated payments:** No real funds are transferred. All actions are simulated locally.
> - **Demo Network Risk Score:** The risk score is a heuristic demonstration index and does not represent a certified banking actuarial probability.
> - **Self-Contained:** Zero dependencies on paid external APIs or cloud services.

---

## 🔭 Limitations & Future Scope

### Current Prototype Scope
- Evaluates transactions locally using NetworkX in-memory graphs.
- Human-in-the-loop analyst feedback logged locally to CSV.
- Transparent rule-assisted Scikit-Learn explainability without mandatory external LLM APIs.

### Future Scope (Scalability Roadmap)
- **Real-Time Stream Processing:** Integration with Apache Kafka / Redpanda for high-throughput (50,000+ TPS) UPI switch event streams.
- **Graph Neural Networks (GNNs):** Implementation of PyTorch Geometric (PyG) for inductive node classification on rapidly morphing mule topologies.
- **Distributed Graph Databases:** Storage backed by Neo4j, Amazon Neptune, or Memgraph for sub-millisecond multi-hop path traversal.
- **Continuous Online Retraining:** Automated active learning pipelines that retrain behavioral models as analysts submit verified fraud feedback.
- **Core Banking & NPCI Integration:** Direct webhook integration with NPCI UPI switch and bank core AML architectures.

---

## 👥 Team
- **Team Name:** [MEGATHON Team Name]
- **Members:**
  - Jissuriya D
  - Harshini S
  - Hemapriya PS
    
- **College / Institution: knowledge Institute of Technology
