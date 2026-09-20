"""
MuleGuard - Explainable UPI Fraud & Mule-Network Intelligence Prototype
MEGATHON'26 - Fusion For Future
"""

import os
import sys
from datetime import datetime
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Auto-bootstrap Streamlit if invoked directly via 'python app.py'
if not st.runtime.exists():
    import subprocess
    print("[MuleGuard] Launching dashboard via Streamlit on http://localhost:8501 ...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.abspath(__file__)] + sys.argv[1:])
    sys.exit(0)

# Ensure project directory is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.data_loader import (
    load_transactions,
    save_transaction,
    log_analyst_feedback,
    load_feedback,
    generate_synthetic_transactions
)
from src.risk_model import TransactionRiskModel
from src.network_engine import NetworkIntelligenceEngine
from src.explainability import generate_explanation, get_factor_impact_breakdown
from src.simulator import LiveTransactionSimulator

# -----------------------------------------------------------------------------
# PAGE CONFIG & ASSETS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MuleGuard | UPI Mule-Network Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(BASE_DIR, "assets", "custom.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SESSION STATE & CACHING
# -----------------------------------------------------------------------------
@st.cache_resource
def get_risk_model():
    return TransactionRiskModel()

@st.cache_resource
def get_network_engine():
    return NetworkIntelligenceEngine()

if "transactions_df" not in st.session_state:
    st.session_state.transactions_df = load_transactions()

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

if "last_sim_result" not in st.session_state:
    st.session_state.last_sim_result = None

# Recalculate ML & Graph scoring on current state
risk_model = get_risk_model()
network_engine = get_network_engine()

# Predict risk on current dataset
scored_df = risk_model.predict_risk(st.session_state.transactions_df)
network_engine.build_graph(scored_df)
detected_networks = network_engine.detect_all_mule_networks(scored_df)
fan_ins = network_engine.detect_fan_in()
fan_outs = network_engine.detect_fan_out()
rapids = network_engine.detect_rapid_forwarding(scored_df)
chains = network_engine.detect_multihop_chains()


# -----------------------------------------------------------------------------
# BRAND HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="brand-header">
    <div>
        <div class="brand-title">
            <span>🛡️</span> MuleGuard
        </div>
        <div class="brand-tagline">
            Explainable UPI Fraud & Coordinated Mule-Network Intelligence
        </div>
    </div>
    <div style="display: flex; align-items: center; gap: 15px;">
        <div class="status-pill-online">
            <div class="pulse-dot"></div>
            SYSTEM ONLINE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & QUICK ACTIONS
# -----------------------------------------------------------------------------
st.sidebar.markdown("### 🛡️ **MuleGuard Core**")
st.sidebar.markdown(
    "<small style='color:#94A3B8;'>Enterprise Threat Intelligence<br>Autonomous UPI Shield</small>",
    unsafe_allow_html=True
)
st.sidebar.divider()

# Quick Scenario Launcher
st.sidebar.markdown("#### ⚡ **Quick Scenario Demo**")
demo_btn = st.sidebar.button("🚀 Load Active Mule Syndicate", use_container_width=True, type="primary")
if demo_btn:
    st.session_state.demo_mode = True
    st.session_state.selected_nav = "🕸️ Network Intelligence"
    st.session_state.selected_net_override = "MG-NET-DEMO-RING"
    st.rerun()

nav_options = [
    "📊 Overview",
    "💳 Transactions",
    "🕸️ Network Intelligence",
    "🚨 Fraud Analyst Alerts",
    "⚠️ Pre-Transfer Warning",
    "🧪 Live Transaction Simulator",
    "🔍 Data & Filters",
    "🏛️ Architecture & Safety"
]

if "selected_nav" not in st.session_state:
    st.session_state.selected_nav = "📊 Overview"

selected_nav = st.sidebar.radio(
    "Navigation",
    nav_options,
    key="selected_nav",
    label_visibility="collapsed"
)

st.sidebar.divider()
st.sidebar.markdown("#### ⚙️ **Dataset Control**")
if st.sidebar.button("🔄 Reset to Clean Synthetic Data", use_container_width=True):
    st.session_state.transactions_df = load_transactions(force_regenerate=True)
    st.session_state.demo_mode = False
    st.session_state.last_sim_result = None
    st.toast("Dataset reset to baseline synthetic state.")
    st.rerun()

st.sidebar.markdown("""
<div style="font-size: 0.72rem; color: #64748B; margin-top: 15px;">
    <b>Demo Safety:</b> Synthetic transactions only. No real banking credentials or live UPI accounts are accessed.
</div>
""", unsafe_allow_html=True)


# =============================================================================
# PAGE 1: 📊 OVERVIEW
# =============================================================================
if selected_nav == "📊 Overview":
    st.markdown("### 📊 Executive Risk & Intelligence Overview")
    st.markdown("<p style='color:#94A3B8;'>Real-time telemetry and network aggregation computed from synthetic UPI transaction flows.</p>", unsafe_allow_html=True)

    # 1. KPI CARDS (Calculated dynamically)
    total_txs = len(scored_df)
    suspicious_txs = len(scored_df[scored_df["risk_level"].isin(["HIGH", "MEDIUM"])])
    high_risk_txs = len(scored_df[scored_df["risk_level"] == "HIGH"])
    
    # Calculate unique high-risk accounts (senders or receivers in HIGH risk txs)
    high_risk_accs = set(scored_df[scored_df["risk_level"] == "HIGH"]["sender_id"]).union(
        set(scored_df[scored_df["risk_level"] == "HIGH"]["receiver_id"])
    )
    mule_nets_count = len(detected_networks)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>💳</span> Total Transactions</div>
            <div class="kpi-value">{total_txs}</div>
            <div class="kpi-subtext">Evaluated synthetic records</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>⚠️</span> Suspicious Transactions</div>
            <div class="kpi-value" style="color:#F59E0B;">{suspicious_txs}</div>
            <div class="kpi-subtext">{round(suspicious_txs/total_txs*100, 1)}% flagged for review</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>🚨</span> High-Risk Accounts</div>
            <div class="kpi-value" style="color:#EF4444;">{len(high_risk_accs)}</div>
            <div class="kpi-subtext">Identified mule candidates</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title"><span>🕸️</span> Mule Networks Detected</div>
            <div class="kpi-value" style="color:#00F5D4;">{mule_nets_count}</div>
            <div class="kpi-subtext">Coordinated syndicates & chains</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. RISK SUMMARY & DISTRIBUTION
    col_chart, col_summary = st.columns([3, 2])

    with col_chart:
        st.markdown("#### 🎯 **Transaction Risk Distribution**")
        risk_counts = scored_df["risk_level"].value_counts().reindex(["LOW", "MEDIUM", "HIGH"], fill_value=0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=["LOW (0–39)", "MEDIUM (40–69)", "HIGH (70–100)"],
                y=[risk_counts["LOW"], risk_counts["MEDIUM"], risk_counts["HIGH"]],
                marker_color=["#10B981", "#F59E0B", "#EF4444"],
                text=[
                    f"{risk_counts['LOW']} ({round(risk_counts['LOW']/total_txs*100)}%)",
                    f"{risk_counts['MEDIUM']} ({round(risk_counts['MEDIUM']/total_txs*100)}%)",
                    f"{risk_counts['HIGH']} ({round(risk_counts['HIGH']/total_txs*100)}%)"
                ],
                textposition="auto"
            )
        ])
        fig.update_layout(
            paper_bgcolor="rgba(17, 24, 39, 0.7)",
            plot_bgcolor="rgba(17, 24, 39, 0.7)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=280,
            xaxis=dict(title="Calibrated Risk Bands", color="#94A3B8"),
            yaxis=dict(title="Transaction Count", color="#94A3B8", showgrid=True, gridcolor="#1F2937"),
            font=dict(color="#F8FAFC", family="Inter, sans-serif")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_summary:
        st.markdown("#### ⚖️ **Action Policy Matrix**")
        st.markdown(f"""
        <div style="background:#111827; border:1px solid #1F2937; border-radius:12px; padding:18px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    <span class="badge-allow">LOW (0–39)</span>
                    <span style="font-size:0.85rem; color:#94A3B8; margin-left:8px;">Standard retail behavior</span>
                </div>
                <div style="font-weight:700; color:#10B981;">ALLOW ({risk_counts['LOW']})</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    <span class="badge-warn">MEDIUM (40–69)</span>
                    <span style="font-size:0.85rem; color:#94A3B8; margin-left:8px;">Counterparty anomalies</span>
                </div>
                <div style="font-weight:700; color:#F59E0B;">WARN ({risk_counts['MEDIUM']})</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span class="badge-block">HIGH (70–100)</span>
                    <span style="font-size:0.85rem; color:#94A3B8; margin-left:8px;">Coordinated mule patterns</span>
                </div>
                <div style="font-weight:700; color:#EF4444;">BLOCK ({risk_counts['HIGH']})</div>
            </div>
            <hr style="border-color:#1F2937; margin:14px 0 10px 0;" />
            <div style="font-size:0.78rem; color:#94A3B8;">
                🛡️ <b>MuleGuard Principle:</b> Rather than blocking solely on amount, MuleGuard blocks transactions that complete high-velocity mule network structures.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🚨 **Detected Coordinated Mule Networks (Live Summary)**")
    
    net_cols = st.columns(min(3, max(1, len(detected_networks))))
    for i, net in enumerate(detected_networks[:3]):
        with net_cols[i % len(net_cols)]:
            st.markdown(f"""
            <div class="alert-card-danger">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-weight:800; color:#EF4444; font-size:0.9rem;">{net['network_id']}</span>
                    <span class="badge-block">SCORE: {net['risk_score']}/100</span>
                </div>
                <div style="font-size:0.8rem; color:#E2E8F0; margin-bottom:6px;">
                    <b>Topology:</b> {net['type']}
                </div>
                <div style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#38BDF8; word-break:break-all; margin-bottom:10px;">
                    {net['accounts_path']}
                </div>
                <div style="font-size:0.75rem; color:#94A3B8;">
                    {'<br>'.join(net['indicators'])}
                </div>
                <div style="margin-top:12px; font-size:0.8rem; font-weight:700; color:#EF4444;">
                    RECOMMENDED: {net['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# PAGE 2: 💳 TRANSACTIONS
# =============================================================================
elif selected_nav == "💳 Transactions":
    st.markdown("### 💳 Synthetic UPI Transactions Ledger")
    st.markdown("<p style='color:#94A3B8;'>Inspected transaction entries scored by Scikit-Learn behavioral ML model and NetworkX graph topology.</p>", unsafe_allow_html=True)

    # Filter controls
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        risk_filter = st.selectbox("Filter Risk Level", ["ALL", "HIGH", "MEDIUM", "LOW"], index=0)
    with f_col2:
        search_query = st.text_input("Search Account ID or TX ID", "").strip()
    with f_col3:
        min_amt, max_amt = st.slider("Amount Range (₹)", 0, 50000, (0, 50000), step=500)

    # Apply filters
    filtered_df = scored_df.copy()
    if risk_filter != "ALL":
        filtered_df = filtered_df[filtered_df["risk_level"] == risk_filter]
    if search_query:
        filtered_df = filtered_df[
            filtered_df["sender_id"].str.contains(search_query, case=False, na=False) |
            filtered_df["receiver_id"].str.contains(search_query, case=False, na=False) |
            filtered_df["transaction_id"].str.contains(search_query, case=False, na=False)
        ]
    filtered_df = filtered_df[
        (filtered_df["amount"] >= min_amt) & (filtered_df["amount"] <= max_amt)
    ]

    st.markdown(f"<small style='color:#94A3B8;'>Showing {len(filtered_df)} of {len(scored_df)} transactions</small>", unsafe_allow_html=True)

    # Display clean table
    display_df = filtered_df[[
        "transaction_id", "timestamp", "sender_id", "receiver_id",
        "amount", "city", "risk_score", "risk_level", "decision"
    ]].copy()
    display_df["amount"] = display_df["amount"].apply(lambda x: f"₹{x:,.2f}")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "transaction_id": st.column_config.TextColumn("Transaction ID", width="small"),
            "timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
            "sender_id": st.column_config.TextColumn("Sender", width="small"),
            "receiver_id": st.column_config.TextColumn("Receiver", width="small"),
            "amount": st.column_config.TextColumn("Amount", width="small"),
            "city": st.column_config.TextColumn("Jurisdiction", width="small"),
            "risk_score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=100, format="%d"),
            "risk_level": st.column_config.TextColumn("Risk Level", width="small"),
            "decision": st.column_config.TextColumn("Decision", width="small")
        }
    )

    # CSV Download
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Filtered Transactions (CSV)",
        data=csv_bytes,
        file_name="muleguard_transactions.csv",
        mime="text/csv"
    )


# =============================================================================
# PAGE 3: 🕸️ NETWORK INTELLIGENCE (THE INNOVATION)
# =============================================================================
elif selected_nav == "🕸️ Network Intelligence":
    st.markdown("### 🕸️ Graph Intelligence & Mule Topology Analysis")
    st.markdown("<p style='color:#94A3B8;'>MuleGuard's core innovation: Mapping transaction flows as a directed graph to expose coordinated fan-in, fan-out, rapid pass-through, and multi-hop layering rings.</p>", unsafe_allow_html=True)

    if st.session_state.demo_mode:
        st.info("⚡ **Active Syndicate Focus:** Coordinated ring **MG-NET-DEMO-RING** (Victims → MULE_CORE_01 → MULE_LAYER_02 → Exit Gateways) is highlighted in the graph.")

    # Highlighting filter
    all_net_ids = ["All Networks"] + [n["network_id"] for n in detected_networks]
    
    default_net_idx = 0
    if st.session_state.get("selected_net_override") in all_net_ids:
        default_net_idx = all_net_ids.index(st.session_state.selected_net_override)
    elif st.session_state.get("demo_mode"):
        for idx, nid in enumerate(all_net_ids):
            if "DEMO" in nid or "MULE_CORE" in nid:
                default_net_idx = idx
                break

    selected_net = st.selectbox("Highlight Syndicate Network", all_net_ids, index=default_net_idx)
    
    highlight_accounts = None
    if selected_net != "All Networks":
        matching = [n for n in detected_networks if n["network_id"] == selected_net]
        if matching:
            highlight_accounts = matching[0]["all_accounts"]
    elif st.session_state.demo_mode:
        matching_demo = [n for n in detected_networks if "DEMO" in n["network_id"] or "MULE_CORE" in n["network_id"]]
        if matching_demo:
            highlight_accounts = matching_demo[0]["all_accounts"]

    # Graph Rendering
    plotly_fig = network_engine.generate_plotly_graph(highlight_network_accounts=highlight_accounts)
    st.plotly_chart(plotly_fig, use_container_width=True)

    # Graph Legend & Explanations
    st.markdown("""
    <div style="display:flex; gap:24px; justify-content:center; background:#111827; border:1px solid #1F2937; padding:12px; border-radius:10px; margin-bottom:20px;">
        <div style="display:flex; align-items:center; gap:8px; font-size:0.82rem;">
            <span style="width:12px; height:12px; border-radius:50%; background:#10B981; display:inline-block;"></span> Normal Account
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:0.82rem;">
            <span style="width:12px; height:12px; border-radius:50%; background:#F59E0B; display:inline-block;"></span> Suspicious Counterparty
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:0.82rem;">
            <span style="width:12px; height:12px; border-radius:50%; background:#EF4444; display:inline-block;"></span> Mule Candidate (Flagged Hub/Hop)
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:0.82rem;">
            <span style="width:12px; height:12px; border-radius:50%; background:#FF007A; display:inline-block;"></span> Selected Active Syndicate
        </div>
    </div>
    """, unsafe_allow_html=True)

    # DETECTED PATTERNS BREAKDOWN
    st.markdown("#### 🔬 **Detected Network Topology Patterns**")
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌀 Fan-In (Pooling)",
        "🌊 Fan-Out (Dispersal)",
        "⚡ Rapid Forwarding",
        "⛓️ Multi-Hop Layering"
    ])

    with tab1:
        st.markdown("**Fan-In Pattern:** Multiple distinct accounts funneling funds to a single collector account within a tight operational window.")
        if fan_ins:
            for fi in fan_ins:
                st.markdown(f"""
                <div class="alert-card-danger">
                    <div style="font-weight:700; color:#EF4444;">🌀 Aggregator Node: {fi['account_id']}</div>
                    <div style="font-size:0.84rem; color:#E2E8F0; margin-top:4px;">{fi['explanation']}</div>
                    <div style="font-size:0.78rem; color:#94A3B8; margin-top:6px;">
                        <b>Source Accounts:</b> {', '.join(fi['senders'])} | <b>Aggregated Inflow:</b> ₹{fi['total_inflow']:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No fan-in patterns identified exceeding threshold.")

    with tab2:
        st.markdown("**Fan-Out Pattern:** A single account receiving pooled money and immediately splitting disbursements across multiple accounts.")
        if fan_outs:
            for fo in fan_outs:
                st.markdown(f"""
                <div class="alert-card-danger">
                    <div style="font-weight:700; color:#EF4444;">🌊 Dispersal Node: {fo['account_id']}</div>
                    <div style="font-size:0.84rem; color:#E2E8F0; margin-top:4px;">{fo['explanation']}</div>
                    <div style="font-size:0.78rem; color:#94A3B8; margin-top:6px;">
                        <b>Recipient Targets:</b> {', '.join(fo['receivers'])} | <b>Total Disbursed:</b> ₹{fo['total_outflow']:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No fan-out patterns identified exceeding threshold.")

    with tab3:
        st.markdown("**Rapid Forwarding Pattern:** Account acts as a pass-through intermediary, forwarding >70% of inbound funds within minutes.")
        if rapids:
            for r in rapids[:4]:
                st.markdown(f"""
                <div class="alert-card-warn">
                    <div style="font-weight:700; color:#F59E0B;">⚡ Pass-Through Mule: {r['account_id']}</div>
                    <div style="font-size:0.84rem; color:#E2E8F0; margin-top:4px;">{r['explanation']}</div>
                    <div style="font-size:0.78rem; color:#94A3B8; margin-top:6px;">
                        Inbound: <b>{r['inbound_tx']}</b> (₹{r['inbound_amount']:,.2f}) ➔ Outbound: <b>{r['outbound_tx']}</b> (₹{r['outbound_amount']:,.2f}) | <b>Delay: {r['time_delay_min']} mins</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No rapid pass-through transfers identified.")

    with tab4:
        st.markdown("**Multi-Hop Layering Chains:** Extended sequential transaction chains designed to obfuscate origin and distance from the victim.")
        if chains:
            for ch in chains[:4]:
                st.markdown(f"""
                <div class="alert-card-danger">
                    <div style="font-weight:700; color:#EF4444;">⛓️ {ch['hop_count']}-Hop Sequence: {ch['chain_str']}</div>
                    <div style="font-size:0.84rem; color:#E2E8F0; margin-top:4px;">{ch['explanation']}</div>
                    <div style="font-size:0.78rem; color:#94A3B8; margin-top:6px;">
                        <b>Entry Origin:</b> {ch['start_node']} ➔ <b>Exit Destination:</b> {ch['end_node']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No multi-hop layering chains identified.")

    # WHY FLAGGED EXPLANATION PANEL
    # WHY FLAGGED EXPLANATION PANEL
    st.markdown("---")
    st.markdown("#### 💡 **Why Flagged? (Interactive Account Inspector)**")
    st.markdown("<p style='color:#94A3B8;'>Inspect any account to view its specific graph risk score, counterparty topology, and plain-language indicators.</p>", unsafe_allow_html=True)

    # Pre-calculate scores for all nodes to rank and display badges
    all_nodes = list(network_engine.G.nodes())
    node_evals = {node: network_engine.compute_network_risk_score(node, scored_df) for node in all_nodes}
    
    # Sort accounts by risk score descending so high-risk mules appear first
    sorted_accounts = sorted(all_nodes, key=lambda n: node_evals[n]["score"], reverse=True)

    # Quick inspection pills
    st.markdown("<small style='color:#94A3B8; font-weight:600;'>QUICK BENCHMARKS:</small>", unsafe_allow_html=True)
    q_cols = st.columns(5)
    with q_cols[0]:
        if st.button("🚨 Hub: M001", use_container_width=True):
            st.session_state.inspected_account_id = "M001"
            st.rerun()
    with q_cols[1]:
        if st.button("🚨 Core: MULE_CORE_01", use_container_width=True):
            st.session_state.inspected_account_id = "MULE_CORE_01"
            st.rerun()
    with q_cols[2]:
        if st.button("⚠️ Forwarder: M005", use_container_width=True):
            st.session_state.inspected_account_id = "M005"
            st.rerun()
    with q_cols[3]:
        if st.button("⚠️ Layering: A101", use_container_width=True):
            st.session_state.inspected_account_id = "A101"
            st.rerun()
    with q_cols[4]:
        if st.button("✅ Genuine: A009", use_container_width=True):
            st.session_state.inspected_account_id = "A009"
            st.rerun()

    # Determine default account index (default to high-risk M001 or session state)
    default_acc_id = st.session_state.get("inspected_account_id", "M001")
    default_acc_idx = sorted_accounts.index(default_acc_id) if default_acc_id in sorted_accounts else 0

    def format_account_label(acc):
        ev = node_evals[acc]
        sc = ev["score"]
        if sc >= 70:
            return f"🚨 {acc} — Risk: {sc}/100 [HIGH RISK MULE]"
        elif sc >= 40:
            return f"⚠️ {acc} — Risk: {sc}/100 [SUSPICIOUS / WARN]"
        else:
            return f"✅ {acc} — Risk: {sc}/100 [NORMAL RETAIL]"

    inspect_account = st.selectbox(
        "Select Account (Ranked by Risk)",
        sorted_accounts,
        index=default_acc_idx,
        format_func=format_account_label,
        key="inspector_selectbox"
    )
    st.session_state.inspected_account_id = inspect_account

    if inspect_account:
        net_score_data = node_evals[inspect_account]
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            score_val = net_score_data['score']
            color_hex = '#EF4444' if score_val >= 70 else '#F59E0B' if score_val >= 40 else '#10B981'
            st.markdown(f"""
            <div style="background:#111827; border:1px solid #1F2937; border-radius:12px; padding:20px; text-align:center;">
                <div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase;">Demo Network Risk Score</div>
                <div style="font-size:3.2rem; font-weight:800; color:{color_hex}; font-family:'JetBrains Mono';">
                    {score_val} <span style="font-size:1.2rem; color:#94A3B8;">/ 100</span>
                </div>
                <div style="margin-top:6px;">
                    <span class="{'badge-block' if score_val>=70 else 'badge-warn' if score_val>=40 else 'badge-allow'}">
                        {net_score_data['level']} ➔ {net_score_data['action']}
                    </span>
                </div>
                <hr style="border-color:#1F2937; margin:14px 0;" />
                <div style="font-size:0.78rem; text-align:left; color:#94A3B8;">
                    <div><b>Inbound Flow:</b> {net_score_data['in_degree']} transfers (₹{network_engine.G.nodes[inspect_account].get('in_amount', 0):,.2f})</div>
                    <div style="margin-top:4px;"><b>Outbound Flow:</b> {net_score_data['out_degree']} transfers (₹{network_engine.G.nodes[inspect_account].get('out_amount', 0):,.2f})</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown("""<div class="explain-panel"><div class="explain-title">🔍 Plain-Language Network Indicators</div>""", unsafe_allow_html=True)
            for factor, pts in net_score_data["breakdown"].items():
                st.markdown(f"<div class='explain-item'>• <b>{factor}:</b> Contributed +{pts} pts to network risk index</div>", unsafe_allow_html=True)
            if not net_score_data["breakdown"]:
                st.markdown("<div class='explain-item'>• Normal baseline connectivity. No coordinated mule signatures detected.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Show Associated Transactions for this account
        acc_txs = scored_df[(scored_df["sender_id"] == inspect_account) | (scored_df["receiver_id"] == inspect_account)]
        if not acc_txs.empty:
            st.markdown(f"<small style='color:#94A3B8;'><b>Associated Transactions for {inspect_account}:</b></small>", unsafe_allow_html=True)
            display_sub_df = acc_txs[["transaction_id", "timestamp", "sender_id", "receiver_id", "amount", "city", "risk_score", "decision"]].copy()
            display_sub_df["amount"] = display_sub_df["amount"].apply(lambda x: f"₹{x:,.2f}")
            st.dataframe(display_sub_df, use_container_width=True, hide_index=True)


# =============================================================================
# PAGE 4: 🚨 FRAUD ANALYST ALERTS & FEEDBACK
# =============================================================================
elif selected_nav == "🚨 Fraud Analyst Alerts":
    st.markdown("### 🚨 Fraud Analyst Investigation & Alert Queue")
    st.markdown("<p style='color:#94A3B8;'>Operational workstation for compliance officers to audit flagged mule rings, review plain-English reasons, and log human decisions.</p>", unsafe_allow_html=True)

    if detected_networks:
        alert_options = [f"{n['network_id']} - {n['type']} (Score: {n['risk_score']})" for n in detected_networks]
        selected_alert_idx = st.selectbox("Select Alert from Queue", range(len(alert_options)), format_func=lambda x: alert_options[x])
        active_alert = detected_networks[selected_alert_idx]

        st.markdown(f"""
        <div class="alert-card-danger" style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:1.25rem; font-weight:800; color:#EF4444;">🚨 HIGH-RISK MULE ALERT: {active_alert['network_id']}</span>
                <span class="badge-block">DEMO NETWORK RISK: {active_alert['risk_score']} / 100</span>
            </div>
            <div style="margin-top:10px; font-size:0.92rem; color:#F8FAFC;">
                <b>Coordinated Path:</b> <span style="font-family:'JetBrains Mono', monospace; color:#38BDF8;">{active_alert['accounts_path']}</span>
            </div>
            <div style="margin-top:6px; font-size:0.85rem; color:#94A3B8;">
                <b>Hub / Focal Account:</b> {active_alert['hub_account']} | <b>Topology Classification:</b> {active_alert['type']}
            </div>
            <hr style="border-color:#374151; margin:12px 0;" />
            <div style="font-size:0.88rem; color:#F8FAFC; font-weight:700; margin-bottom:6px;">Observed Network Indicators:</div>
            <div style="font-size:0.84rem; color:#E2E8F0; line-height:1.6;">
                {'<br>'.join(active_alert['indicators'])}
            </div>
            <div style="margin-top:14px; font-size:0.95rem; font-weight:800; color:#EF4444;">
                RECOMMENDED SYSTEM ACTION: 🔴 BLOCK
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Plain-English Explainability Box
        st.markdown("#### 💡 **Explainable AI (Plain-English Diagnostics)**")
        
        # Get representative transaction for hub account
        hub_txs = scored_df[(scored_df["sender_id"] == active_alert["hub_account"]) | (scored_df["receiver_id"] == active_alert["hub_account"])]
        rep_tx = hub_txs.iloc[0].to_dict() if not hub_txs.empty else {"amount": 5000, "sender_id": "A101", "receiver_id": active_alert["hub_account"]}
        
        graph_metrics = {
            "unique_senders": network_engine.G.in_degree(active_alert["hub_account"]) if active_alert["hub_account"] in network_engine.G else 3,
            "unique_receivers": network_engine.G.out_degree(active_alert["hub_account"]) if active_alert["hub_account"] in network_engine.G else 2,
            "forwarding_delay_min": 8.5,
            "retention_ratio": 92.0
        }
        
        reasons = generate_explanation(rep_tx, graph_metrics, [active_alert["type"]])
        st.markdown("""<div class="explain-panel"><div class="explain-title">🛡️ Plain-Language Evidence</div>""", unsafe_allow_html=True)
        for r in reasons:
            st.markdown(f"<div class='explain-item'>• {r}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Factor Impact Table
        st.markdown("#### 📊 **Transparent Factor Impact Breakdown**")
        factor_df = get_factor_impact_breakdown(rep_tx, graph_metrics)
        st.dataframe(factor_df, use_container_width=True, hide_index=True)

        # ANALYST FEEDBACK WORKFLOW
        st.markdown("---")
        st.markdown("#### ✍️ **Human-in-the-Loop Analyst Feedback**")
        st.markdown("<small style='color:#94A3B8;'>Analyst decisions are audited and persisted to <code>data/feedback.csv</code> for future model governance.</small>", unsafe_allow_html=True)

        fb_notes = st.text_input("Analyst Audit Notes", placeholder="e.g. Confirmed coordinated layering pattern matching Jamtara syndicate modus operandi.")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            if st.button("🚨 Confirm Fraud & Block Syndicate", use_container_width=True, type="primary"):
                tx_ref = rep_tx.get("transaction_id", "NET_REF")
                log_analyst_feedback(
                    tx_id=tx_ref,
                    account_id=active_alert["hub_account"],
                    network_id=active_alert["network_id"],
                    decision="CONFIRMED_FRAUD",
                    notes=fb_notes if fb_notes else "Analyst confirmed coordinated mule ring.",
                    risk_score=active_alert["risk_score"]
                )
                st.success(f"Feedback recorded: {active_alert['network_id']} confirmed as FRAUD. Saved to data/feedback.csv for future model improvement.")
        
        with f_col2:
            if st.button("✅ Mark Genuine (False Positive)", use_container_width=True):
                tx_ref = rep_tx.get("transaction_id", "NET_REF")
                log_analyst_feedback(
                    tx_id=tx_ref,
                    account_id=active_alert["hub_account"],
                    network_id=active_alert["network_id"],
                    decision="GENUINE",
                    notes=fb_notes if fb_notes else "Verified as legitimate commercial distributor flow.",
                    risk_score=active_alert["risk_score"]
                )
                st.info(f"Feedback recorded: Marked as GENUINE. Saved to data/feedback.csv.")

        # Show audit log
        st.markdown("##### 📜 **Analyst Feedback Audit Trail**")
        feedback_df = load_feedback()
        if not feedback_df.empty:
            st.dataframe(feedback_df.tail(5), use_container_width=True, hide_index=True)
        else:
            st.caption("No feedback logged yet in this session.")

    else:
        st.info("No active high-risk alerts in queue.")


# =============================================================================
# PAGE 5: ⚠️ PRE-TRANSFER WARNING (CUSTOMER PROTECTION SIMULATION)
# =============================================================================
elif selected_nav == "⚠️ Pre-Transfer Warning":
    st.markdown("### ⚠️ Simulated Customer Pre-Transfer Protection Screen")
    st.markdown("<p style='color:#94A3B8;'>Demonstrates how MuleGuard intercepts a high-risk payment inside a consumer UPI mobile app before funds depart.</p>", unsafe_allow_html=True)

    # Preset selection or custom
    preset_choice = st.selectbox(
        "Choose Simulated Customer Transfer Scenario",
        [
            "Scenario 1: Transfer ₹8,500 to Aggregator Mule M001",
            "Scenario 2: Transfer ₹10,000 to Pass-Through Mule M005",
            "Scenario 3: Transfer ₹42,000 to Layering Node MULE_LAYER_02",
            "Scenario 4: Transfer ₹450 to Genuine Friend B002"
        ]
    )

    if "Scenario 1" in preset_choice:
        recipient = "M001"
        amt = 8500.0
        risk_lvl = "HIGH"
        score = 84
        why_text = "This recipient is connected to a suspicious chain of rapidly forwarded transactions with multiple unrelated senders."
    elif "Scenario 2" in preset_choice:
        recipient = "M005"
        amt = 10000.0
        risk_lvl = "HIGH"
        score = 89
        why_text = "This recipient account has a history of immediately re-routing 95% of incoming funds to external accounts within minutes."
    elif "Scenario 3" in preset_choice:
        recipient = "MULE_LAYER_02"
        amt = 42000.0
        risk_lvl = "HIGH"
        score = 94
        why_text = "Recipient is identified as a layer-2 aggregator node connected to high-risk offshore UPI and OTC settlement gateways."
    else:
        recipient = "B002"
        amt = 450.0
        risk_lvl = "LOW"
        score = 12
        why_text = "Recipient exhibits standard peer-to-peer transaction history with no network anomalies."

    st.markdown(f"""
    <div class="transfer-warning-card">
        <div style="font-size:2.8rem; margin-bottom:8px;">⚠️</div>
        <div class="transfer-warning-title">Before You Transfer</div>
        <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:16px;">
            MuleGuard Real-Time UPI Shield (Simulated Consumer Screen)
        </div>
        <div style="background:rgba(255,255,255,0.05); border-radius:12px; padding:18px; text-align:left; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:#94A3B8;">Recipient UPI ID:</span>
                <span style="font-weight:700; color:#F8FAFC; font-family:'JetBrains Mono';">{recipient.lower()}@okaxis</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:#94A3B8;">Transfer Amount:</span>
                <span style="font-weight:800; color:#FFFFFF; font-size:1.15rem;">₹{amt:,.2f}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:#94A3B8;">Mule-Network Risk:</span>
                <span style="font-weight:800; color:{'#EF4444' if risk_lvl=='HIGH' else '#10B981'};">{risk_lvl} ({score} / 100)</span>
            </div>
            <hr style="border-color:#2A3852; margin:10px 0;" />
            <div style="color:#94A3B8; font-size:0.82rem; margin-bottom:4px;">Why Flagged?</div>
            <div style="color:#FCA5A5; font-size:0.88rem; line-height:1.4;">
                "{why_text}"
            </div>
        </div>
        <div style="font-size:0.75rem; color:#64748B; margin-bottom:15px;">
            ⚠️ SIMULATION ONLY. This screen demonstrates explainable friction to prevent victim coercion.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔴 Cancel Transfer (Recommended)", use_container_width=True, type="primary"):
            st.error("Transfer safely aborted by user. Potential mule network loss prevented!")
    with col_btn2:
        if st.button("🟢 Proceed Anyway (User Override)", use_container_width=True):
            st.warning("User elected to proceed. Step-up 2FA biometric confirmation triggered.")


# =============================================================================
# PAGE 6: 🧪 LIVE TRANSACTION SIMULATOR
# =============================================================================
elif selected_nav == "🧪 Live Transaction Simulator":
    st.markdown("### 🧪 Live Transaction Simulator")
    st.markdown("<p style='color:#94A3B8;'>Inject a simulated UPI transaction on-the-fly and observe immediate ML scoring, graph recalculation, explainability generation, and action decision.</p>", unsafe_allow_html=True)
    st.info("ℹ️ **Simulated transaction — no real money is involved.**")

    sim = LiveTransactionSimulator(risk_model=risk_model, network_engine=network_engine)

    with st.form("simulation_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            sim_sender = st.text_input("Sender Account ID", "VICTIM_NEW_01")
        with col2:
            sim_receiver = st.text_input("Receiver Account ID", "M001")
        with col3:
            sim_amount = st.number_input("Amount (₹)", min_value=10.0, max_value=200000.0, value=7500.0, step=500.0)

        col4, col5 = st.columns(2)
        with col4:
            sim_city = st.selectbox("Location / Jurisdiction", ["Bengaluru", "Mumbai", "Delhi", "Jamtara", "Deoghar", "Alwar", "Dubai_UPI_Gateway"])
        with col5:
            sim_channel = st.selectbox("Payment Channel", ["P2P", "P2M"])

        submit_sim = st.form_submit_button("⚡ Run Live MuleGuard Evaluation", use_container_width=True, type="primary")

    if submit_sim:
        with st.spinner("Processing transaction through ML & Graph Intelligence Pipeline..."):
            res = sim.simulate_transaction(
                sender_id=sim_sender,
                receiver_id=sim_receiver,
                amount=sim_amount,
                city=sim_city,
                channel=sim_channel,
                current_df=scored_df
            )
            st.session_state.last_sim_result = res

    if st.session_state.last_sim_result:
        res = st.session_state.last_sim_result
        tx = res["transaction"]

        st.markdown("---")
        st.markdown("#### 📋 **Simulation Evaluation Results**")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">ML Anomaly Score</div>
                <div class="kpi-value">{res['ml_score']} / 100</div>
                <div class="kpi-subtext">Scikit-Learn Random Forest</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Demo Network Risk</div>
                <div class="kpi-value">{res['network_score']} / 100</div>
                <div class="kpi-subtext">NetworkX Graph Topology</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            dec_color = "#EF4444" if res['decision'] == "BLOCK" else "#F59E0B" if res['decision'] == "WARN" else "#10B981"
            st.markdown(f"""
            <div class="kpi-card" style="border-color:{dec_color};">
                <div class="kpi-title">Final Decision</div>
                <div class="kpi-value" style="color:{dec_color};">{res['decision']}</div>
                <div class="kpi-subtext">Composite Score: {res['composite_score']}/100</div>
            </div>
            """, unsafe_allow_html=True)

        # Plain-English Explanation
        st.markdown("""<div class="explain-panel"><div class="explain-title">🔍 Generated Explainability Statement</div>""", unsafe_allow_html=True)
        for r in res["reasons"]:
            st.markdown(f"<div class='explain-item'>• {r}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Factor table
        st.markdown("##### 📊 **Factor Impact Matrix**")
        st.dataframe(res["factor_breakdown"], use_container_width=True, hide_index=True)

        # Commit to session button
        if st.button("➕ Commit Transaction to Active Session Dataset", use_container_width=True):
            save_transaction(tx)
            st.session_state.transactions_df = load_transactions()
            st.success("Transaction committed! Updated transaction graph and dashboard metrics.")
            st.rerun()


# =============================================================================
# PAGE 7: 🔍 DATA & FILTERS
# =============================================================================
elif selected_nav == "🔍 Data & Filters":
    st.markdown("### 🔍 Raw Transaction Data & Subgraph Filters")
    st.markdown("<p style='color:#94A3B8;'>Direct access to explore underlying synthetic dataset, inspect node attributes, and audit network memberships.</p>", unsafe_allow_html=True)

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        sel_account = st.selectbox("Inspect Account Records", ["All Accounts"] + sorted(list(network_engine.G.nodes())))
    with d_col2:
        sel_tag = st.selectbox("Filter Pattern Tag", ["ALL"] + sorted(list(scored_df["pattern_tag"].unique())))

    view_df = scored_df.copy()
    if sel_account != "All Accounts":
        view_df = view_df[(view_df["sender_id"] == sel_account) | (view_df["receiver_id"] == sel_account)]
    if sel_tag != "ALL":
        view_df = view_df[view_df["pattern_tag"] == sel_tag]

    st.dataframe(view_df, use_container_width=True)


# =============================================================================
# PAGE 8: 🏛️ ARCHITECTURE & SAFETY
# =============================================================================
elif selected_nav == "🏛️ Architecture & Safety":
    st.markdown("### 🏛️ Solution Architecture & Engineering Design")
    st.markdown("<p style='color:#94A3B8;'>Technical design specification for MEGATHON'26 – Fusion For Future.</p>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#111827; border:1px solid #1F2937; border-radius:14px; padding:24px; margin-bottom:24px;">
        <h4 style="color:#00F5D4; margin-top:0;">🔄 End-to-End Processing Pipeline</h4>
        <div style="display:flex; flex-direction:column; gap:10px; font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#E2E8F0;">
            <div>1. <b>Synthetic UPI Transactions:</b> Ingestion of high-velocity peer-to-peer and merchant payments.</div>
            <div style="color:#94A3B8;">&nbsp;&nbsp;&nbsp;&nbsp;↓</div>
            <div>2. <b>Feature Engineering:</b> Temporal window aggregations, counterparty velocity, and turnaround time ratios.</div>
            <div style="color:#94A3B8;">&nbsp;&nbsp;&nbsp;&nbsp;↓</div>
            <div>3. <b>Scikit-Learn ML Risk Model:</b> Calibrated classification of individual transaction anomalies.</div>
            <div style="color:#94A3B8;">&nbsp;&nbsp;&nbsp;&nbsp;↓</div>
            <div>4. <b>NetworkX Transaction Graph:</b> Directed multigraph representation connecting senders and receivers.</div>
            <div style="color:#94A3B8;">&nbsp;&nbsp;&nbsp;&nbsp;↓</div>
            <div>5. <b>Mule Pattern Engine:</b> Heuristic and topological detectors for Fan-In, Fan-Out, Rapid Forwarding, and Multi-Hop Layering.</div>
            <div style="color:#94A3B8;">&nbsp;&nbsp;&nbsp;&nbsp;↓</div>
            <div>6. <b>Explainability Layer:</b> Plain-language translation (generate_explanation) converting graph indicators to readable evidence.</div>
            <div style="color:#94A3B8;">&nbsp;&nbsp;&nbsp;&nbsp;↓</div>
            <div>7. <b>Decision Engine:</b> Action policies: 0-39 ALLOW | 40-69 WARN | 70-100 BLOCK.</div>
            <div style="color:#94A3B8;">&nbsp;&nbsp;&nbsp;&nbsp;↓</div>
            <div>8. <b>Analyst & Customer Interfaces:</b> Dual-tier dispatching to customer pre-transfer screens and compliance alert queue.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_fut, col_safe = st.columns(2)

    with col_fut:
        st.markdown("""
        <div style="background:#111827; border:1px solid #1F2937; border-radius:14px; padding:20px; height:100%;">
            <h4 style="color:#38BDF8; margin-top:0;">🚀 Future Scope (Scalability Roadmap)</h4>
            <ul style="font-size:0.85rem; color:#CBD5E1; line-height:1.7;">
                <li><b>Real-Time Event Streaming:</b> Distributed transaction ingestion via Apache Kafka or Redpanda.</li>
                <li><b>Graph Neural Networks (GNNs):</b> PyTorch Geometric (PyG) for inductive representation learning on evolving graphs.</li>
                <li><b>Production Graph Database:</b> Neo4j or Amazon Neptune integration for millisecond multi-hop path traversals.</li>
                <li><b>Automated Model Retraining:</b> Continual active learning pipeline driven by human analyst feedback logs.</li>
                <li><b>Banking NPCI / Bank Core Integration:</b> Direct API hooks with UPI Switch (NPCI) and banking AML core.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_safe:
        st.markdown("""
        <div style="background:#111827; border:1px solid #1F2937; border-radius:14px; padding:20px; height:100%;">
            <h4 style="color:#10B981; margin-top:0;">🛡️ Demo Safety & Privacy Notice</h4>
            <ul style="font-size:0.85rem; color:#CBD5E1; line-height:1.7;">
                <li><b>Synthetic Transaction Data Only:</b> All transactions, UPI IDs, and account numbers are synthetically generated.</li>
                <li><b>No Real Financial Data:</b> Zero access to real banking databases, customer PII, or live financial accounts.</li>
                <li><b>No Live Payment Execution:</b> No money moves; all transactions and actions are simulated within the local runtime.</li>
                <li><b>Zero Cloud API Lock-in:</b> Completely self-contained, runs 100% offline on standard CPU without paid APIs.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🛡️ **Enterprise Architecture & System Capabilities**")
    st.markdown("""
    | Core Capability | MuleGuard Enterprise Implementation |
    | :--- | :--- |
    | **Coordinated Syndicate Detection** | Solves multi-tier mule syndicates bypassing traditional single-transaction rules. |
    | **Dual Graph & Behavioral AI** | Combines ML anomaly scoring with NetworkX topological pattern mining (fan-in, fan-out, rapid forwarding, multi-hop). |
    | **Explainable Auditability** | Plain-language evidence translation paired with human-in-the-loop analyst feedback persistence. |
    | **Consumer & Analyst Protection** | Pre-transfer friction for mobile banking apps alongside operational analyst alert queues. |
    | **Ultra-Lightweight & Scalable** | High-performance, self-contained architecture running locally without external API dependencies. |
    | **Modern Threat Visualization** | Interactive topological graph mapping with real-time risk indicators and color-coded entity states. |
    """)
