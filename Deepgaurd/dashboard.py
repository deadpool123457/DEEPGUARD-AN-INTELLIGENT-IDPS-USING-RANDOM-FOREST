import os
os.environ['STREAMLIT_LOG_LEVEL'] = 'error'
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time, warnings, psutil
from datetime import datetime, timedelta
import json
import uuid
import sqlite3
import subprocess

warnings.filterwarnings("ignore")
st.set_page_config(page_title="🛡️ DEEPGUARD IDPS", layout="wide", initial_sidebar_state="collapsed")

# --- ENHANCED CYBER CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
    
    /* Main App Styling */
    .stApp { 
        background: linear-gradient(135deg, #0a0a0a 0%, #001a00 100%);
        color: #00FF41; 
        font-family: 'Orbitron', sans-serif;
    }
    
    /* Animated Header */
    .header { 
        text-align: center; 
        border: 3px solid #00FF41; 
        padding: 25px; 
        background: linear-gradient(135deg, rgba(0,50,0,0.9) 0%, rgba(0,20,0,0.9) 100%);
        margin-bottom: 30px; 
        border-radius: 15px;
        box-shadow: 0 0 30px rgba(0,255,65,0.3), inset 0 0 20px rgba(0,255,65,0.1);
        animation: headerGlow 3s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(0,255,65,0.1), transparent);
        animation: scan 4s linear infinite;
    }
    
    @keyframes headerGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(0,255,65,0.3), inset 0 0 20px rgba(0,255,65,0.1); }
        50% { box-shadow: 0 0 40px rgba(0,255,65,0.5), inset 0 0 30px rgba(0,255,65,0.2); }
    }
    
    @keyframes scan {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
    
    h1 { 
        color: #fff; 
        text-shadow: 0 0 20px #00FF41, 0 0 40px #00FF41; 
        margin: 0;
        font-weight: 900;
        letter-spacing: 3px;
        animation: titlePulse 2s ease-in-out infinite;
    }
    
    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .version { 
        color: #00FF41; 
        font-size: 14px; 
        font-family: 'Share Tech Mono', monospace;
        opacity: 0.8;
        letter-spacing: 2px;
    }
    
    /* Enhanced Metrics */
    div[data-testid="stMetricValue"] { 
        color: #00FF41 !important; 
        font-size: 32px !important;
        font-weight: 900 !important;
        text-shadow: 0 0 10px #00FF41;
        animation: metricGlow 2s ease-in-out infinite;
    }
    
    @keyframes metricGlow {
        0%, 100% { text-shadow: 0 0 10px #00FF41; }
        50% { text-shadow: 0 0 20px #00FF41, 0 0 30px #00FF41; }
    }
    
    div[data-testid="stMetricLabel"] { 
        color: #aaa !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
    }
    
    div[data-testid="stMetricDelta"] {
        color: #ff0000 !important;
        font-weight: 700 !important;
    }
    
    /* Glowing Cards */
    .element-container {
        background: rgba(0,20,0,0.3);
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(0,255,65,0.2);
    }
    
    /* Risk Box with Animation */
    .risk-box { 
        border: 2px solid #00FF41; 
        padding: 20px; 
        background: linear-gradient(135deg, rgba(0,40,0,0.8) 0%, rgba(0,20,0,0.8) 100%);
        margin-top: 10px; 
        border-radius: 10px; 
        color: #ccc;
        box-shadow: 0 0 20px rgba(0,255,65,0.2);
        animation: boxPulse 3s ease-in-out infinite;
    }
    
    @keyframes boxPulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0,255,65,0.2); }
        50% { box-shadow: 0 0 30px rgba(0,255,65,0.4); }
    }
    
    /* Critical Alert with Strong Animation */
    .alert-banner { 
        background: linear-gradient(135deg, #440000 0%, #220000 100%);
        border: 3px solid #ff0000; 
        padding: 15px; 
        border-radius: 10px; 
        margin: 15px 0;
        box-shadow: 0 0 30px rgba(255,0,0,0.5);
        animation: criticalPulse 1s ease-in-out infinite;
        font-weight: 900;
        font-size: 16px;
    }
    
    @keyframes criticalPulse { 
        0%, 100% { 
            opacity: 1; 
            box-shadow: 0 0 30px rgba(255,0,0,0.5);
            transform: scale(1);
        } 
        50% { 
            opacity: 0.85; 
            box-shadow: 0 0 50px rgba(255,0,0,0.8);
            transform: scale(1.01);
        } 
    }
    
    /* Subheaders with Glow */
    .stMarkdown h2, .stMarkdown h3 {
        color: #00FF41 !important;
        text-shadow: 0 0 15px #00FF41;
        letter-spacing: 2px;
        border-bottom: 2px solid rgba(0,255,65,0.3);
        padding-bottom: 10px;
        margin-top: 20px;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(0,20,0,0.5);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(0,40,0,0.5);
        border: 1px solid rgba(0,255,65,0.3);
        border-radius: 8px;
        color: #00FF41;
        font-weight: 700;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0,60,0,0.7);
        box-shadow: 0 0 15px rgba(0,255,65,0.3);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,80,0,0.9) 0%, rgba(0,60,0,0.9) 100%) !important;
        border: 2px solid #00FF41 !important;
        box-shadow: 0 0 20px rgba(0,255,65,0.5) !important;
    }
    
    /* Radio Buttons */
    .stRadio > label {
        color: #00FF41 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        letter-spacing: 1px;
    }
    
    /* DataFrames */
    .stDataFrame {
        border: 1px solid rgba(0,255,65,0.3);
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0,255,65,0.1);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00FF41 0%, #00AA2B 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00FF41;
        box-shadow: 0 0 10px #00FF41;
    }
    
    /* IP Address Styling */
    code {
        background: rgba(0,60,0,0.5) !important;
        color: #00FF41 !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        border: 1px solid rgba(0,255,65,0.3) !important;
        font-family: 'Share Tech Mono', monospace !important;
    }
    
    /* Success/Warning Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(0,80,0,0.8) 0%, rgba(0,60,0,0.8) 100%) !important;
        border: 2px solid #00FF41 !important;
        box-shadow: 0 0 20px rgba(0,255,65,0.3) !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(80,60,0,0.8) 0%, rgba(60,40,0,0.8) 100%) !important;
        border: 2px solid #ffaa00 !important;
        box-shadow: 0 0 20px rgba(255,170,0,0.3) !important;
    }
    
    /* Corner Decorations */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100px;
        height: 100px;
        border-top: 3px solid #00FF41;
        border-left: 3px solid #00FF41;
        opacity: 0.3;
        pointer-events: none;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        bottom: 0;
        right: 0;
        width: 100px;
        height: 100px;
        border-bottom: 3px solid #00FF41;
        border-right: 3px solid #00FF41;
        opacity: 0.3;
        pointer-events: none;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class='header'>
    <h1>🛡️ DEEPGUARD v2.0 // INTELLIGENT IDPS</h1>
    <div class='version'>⚡ ENHANCED: AUTO-UNBLOCK | ADVANCED ANALYTICS | MULTI-FACTOR RISK SCORING ⚡</div>
</div>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def load_blocked_metadata():
    """Load metadata about blocked IPs"""
    if os.path.exists('blocked_ips_metadata.json'):
        try:
            with open('blocked_ips_metadata.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def ultra_safe_read_sql(filepath):
    """Ultra-robust SQL reader"""
    try:
        conn = sqlite3.connect(filepath)
        df = pd.read_sql("SELECT * FROM logs ORDER BY id DESC LIMIT 2000", conn)
        conn.close()
        if len(df) > 0:
            return standardize_dataframe(df)
    except Exception as e:
        pass
    return None

def standardize_dataframe(df):
    """Ensure DataFrame has all required columns with correct types"""
    required = {
        'Timestamp': '',
        'Source_IP': '0.0.0.0',
        'Destination_IP': '0.0.0.0',
        'Protocol': 'unknown',
        'Length': 0,
        'Status': 'Unknown',
        'country': 'Unknown',
        'lat': 0.0,
        'lon': 0.0,
        'Severity': 'UNKNOWN',
        'Threat_Type': 'Unknown'
    }
    
    for col, default in required.items():
        if col not in df.columns:
            df[col] = default
    
    try:
        df['Length'] = pd.to_numeric(df['Length'], errors='coerce').fillna(0).astype(int)
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce').fillna(0).astype(float)
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce').fillna(0).astype(float)
    except:
        pass
    
    return df

def calculate_risk_score(df, attacks, blocked_count):
    """Calculate risk score"""
    if df is None or df.empty or attacks.empty:
        return 0
    
    score = min(100, len(attacks) * 3 + blocked_count * 2)
    return score

def get_risk_level_text(score):
    """Get risk level description"""
    if score >= 80:
        return "🔴 CRITICAL - Active Attack"
    elif score >= 60:
        return "🟠 HIGH - Sustained Threat"
    elif score >= 40:
        return "🟡 ELEVATED - Suspicious"
    elif score >= 20:
        return "🟢 GUARDED - Minor Threats"
    else:
        return "🟢 LOW - Normal"

# --- MODE SWITCH ---
c_mode, c_stat = st.columns([1, 3])
with c_mode:
    mode = st.radio("⚙️ SYSTEM MODE:", ["MONITOR (IDS)", "ACTIVE BLOCKING (IPS)"], index=1, key="mode_radio")
    with open('mode.txt', 'w') as f: 
        f.write("MONITOR" if "MONITOR" in mode else "ACTIVE")

with c_stat:
    if "ACTIVE" in mode: 
        st.success("✅ **IPS ACTIVE: AUTOMATIC BLOCKING ENGAGED**")
    else: 
        st.warning("⚠️ **IDS MODE: LOGGING ONLY (NO BLOCKING)**")

# Removed while True loop for st.rerun compatibility
if True:
    if True:
        # --- ADMIN CONTROLS ---
        with st.sidebar:
            st.header("🛠️ Admin Controls")
            if st.button("🚨 Emergency Unblock All"):
                if os.path.exists('blocked_ips.txt'):
                    with open('blocked_ips.txt', 'r') as f:
                        ips = f.readlines()
                    for ip in ips:
                        ip = ip.strip()
                        cmd = f"netsh advfirewall firewall delete rule name=\"Deepguard_Block_{ip}\""
                        try:
                            subprocess.run(cmd, shell=True, check=True)
                        except: pass
                    # Clear files
                    open('blocked_ips.txt', 'w').close()
                    with open('blocked_ips_metadata.json', 'w') as f: json.dump({}, f)
                st.success("All IPs Unblocked!")
            
            if st.button("🗑️ Flush Logs Database"):
                try:
                    conn = sqlite3.connect('deepguard_logs.db')
                    conn.cursor().execute("DELETE FROM logs")
                    conn.commit()
                    conn.close()
                    st.success("Logs Cleared!")
                except:
                    pass
        
        if os.path.exists('deepguard_logs.db'):
            df = ultra_safe_read_sql('deepguard_logs.db')
            
            if df is None or df.empty:
                st.info("🟢 No logs available. Everything is quiet.")
                time.sleep(2)
                st.rerun()
            
            try:
                attacks = df[df['Status'].str.upper() == 'MALICIOUS']
                total_p = len(df)
                threats = len(attacks)
                
                # READ BLOCKED LIST
                blocked_list = []
                blocked_metadata = load_blocked_metadata()
                
                if os.path.exists('blocked_ips.txt'):
                    with open('blocked_ips.txt', 'r') as f:
                        blocked_list = list(set([line.strip() for line in f if line.strip()]))

                # CALCULATE RISK
                risk_val = calculate_risk_score(df, attacks, len(blocked_list))
                risk_text = get_risk_level_text(risk_val)

                # ALERT BANNER
                if risk_val > 70:
                    st.markdown(f"""
                    <div class="alert-banner">
                        🚨 <b>SECURITY ALERT:</b> Critical threat level detected! {len(blocked_list)} IPs blocked. Immediate action required!
                    </div>
                    """, unsafe_allow_html=True)

                # HUD METRICS
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("🖥️ CPU", f"{psutil.cpu_percent():.1f}%")
                c2.metric("💾 RAM", f"{psutil.virtual_memory().percent:.1f}%")
                c3.metric("📊 PACKETS", f"{total_p:,}")
                c4.metric("⚠️ THREATS", threats, delta=f"+{threats}" if threats > 0 else "None")
                c5.metric("🚫 BLOCKED", len(blocked_list), delta="ACTIVE" if len(blocked_list) > 0 else "Clean")

                # MAIN DASHBOARD
                col_map, col_risk = st.columns([2.5, 1])
                
                with col_map:
                    st.subheader("🌍 LIVE THREAT MAP")
                    if not attacks.empty:
                        map_data = attacks[(attacks['lat'] != 0) | (attacks['lon'] != 0)]
                        
                        if not map_data.empty:
                            fig_map = px.scatter_mapbox(
                                map_data, 
                                lat="lat", 
                                lon="lon",
                                color="Protocol",
                                size="Length",
                                hover_name="Source_IP",
                                color_discrete_sequence=["#ff0000", "#ff4400", "#ff8800"],
                                zoom=1, 
                                height=450
                            )
                            fig_map.update_layout(
                                mapbox_style="carto-darkmatter", 
                                margin={"r":0,"t":0,"l":0,"b":0},
                                paper_bgcolor="#000",
                                plot_bgcolor="#000"
                            )
                            # Use constant key to prevent re-rendering and flickering during st.rerun
                            st.plotly_chart(fig_map, use_container_width=True, key="live_threat_map")
                        else:
                            st.info("🟢 No geolocated threats (Local traffic only)")
                    else: 
                        st.info("🟢 NO THREATS DETECTED")

                with col_risk:
                    st.subheader("🧠 RISK ANALYSIS")
                    
                    gauge_color = "#ff0000" if risk_val > 70 else "#ff8800" if risk_val > 40 else "#00ff00"
                    fig_g = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=risk_val,
                        title={'text': "THREAT LEVEL", 'font': {'size': 20, 'color': '#00FF41'}},
                        delta={'reference': 30, 'increasing': {'color': "#ff0000"}},
                        number={'font': {'size': 40, 'color': gauge_color}},
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': "#00FF41", 'tickwidth': 2},
                            'bar': {'color': gauge_color, 'thickness': 0.75},
                            'bgcolor': "#000",
                            'borderwidth': 3,
                            'bordercolor': "#00FF41",
                            'steps': [
                                {'range': [0, 20], 'color': 'rgba(0,60,0,0.5)'},
                                {'range': [20, 40], 'color': 'rgba(0,80,0,0.5)'},
                                {'range': [40, 60], 'color': 'rgba(80,60,0,0.5)'},
                                {'range': [60, 80], 'color': 'rgba(100,40,0,0.5)'},
                                {'range': [80, 100], 'color': 'rgba(60,0,0,0.5)'}
                            ],
                            'threshold': {
                                'line': {'color': "white", 'width': 5},
                                'thickness': 0.85,
                                'value': risk_val
                            }
                        }
                    ))
                    fig_g.update_layout(
                        height=280,
                        margin={'t':40,'b':10,'l':20,'r':20}, 
                        paper_bgcolor="#000000",
                        font={'color': "#00FF41", 'size': 14}
                    )
                    # Use constant key 
                    st.plotly_chart(fig_g, use_container_width=True, key="live_risk_gauge")
                    
                    st.markdown(f"""
                    <div class="risk-box">
                        <b>📊 RISK FACTORS:</b><br>
                        • Attack Frequency: {len(attacks)}<br>
                        • Blocked IPs: {len(blocked_list)}<br>
                        • Active Threats: {threats}<br>
                        <hr style="border-color: rgba(0,255,65,0.3);">
                        <b>⚡ CURRENT STATUS:</b><br>
                        <span style="font-size: 18px;">{risk_text}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # VISUALIZATIONS
                st.subheader("📊 ADVANCED ANALYTICS")
                
                viz_col1, viz_col2 = st.columns(2)
                
                with viz_col1:
                    if not attacks.empty and 'Protocol' in attacks.columns:
                        proto_counts = attacks['Protocol'].value_counts()
                        
                        fig_proto = go.Figure(data=[go.Pie(
                            labels=proto_counts.index,
                            values=proto_counts.values,
                            hole=0.5,
                            marker=dict(colors=['#ff0000', '#ff4400', '#ff8800', '#ffcc00']),
                            textfont=dict(size=14, color='white')
                        )])
                        fig_proto.update_layout(
                            title={'text': "Protocol Distribution", 'font': {'size': 18, 'color': '#00FF41'}},
                            height=320,
                            paper_bgcolor="#000",
                            plot_bgcolor="#000",
                            font=dict(color="#00FF41", size=12),
                            showlegend=True,
                            legend=dict(bgcolor="rgba(0,40,0,0.5)", bordercolor="#00FF41", borderwidth=1)
                        )
                        # Use constant key
                        st.plotly_chart(fig_proto, use_container_width=True, key="live_proto_pie")
                
                with viz_col2:
                    st.markdown("### 🎯 TOP ATTACKERS")
                    if not attacks.empty and 'Source_IP' in attacks.columns:
                        top_ips = attacks['Source_IP'].value_counts().head(8)
                        for i, (ip, count) in enumerate(top_ips.items(), 1):
                            severity = "🔴" if count > 50 else "🟠" if count > 20 else "🟡"
                            st.markdown(f"{severity} **#{i}** `{ip}` — **{count}** attacks")
                    else:
                        st.info("No attacker data available")

                # TABS
                t1, t2, t3 = st.tabs(["🚫 BLOCKED IPs", "📜 LIVE FORENSICS", "⏰ AUTO-UNBLOCK STATUS"])
                
                with t1:
                    st.markdown("### 🔒 FIREWALL BLOCKLIST")
                    if blocked_list:
                        for i, ip in enumerate(blocked_list, 1):
                            meta = blocked_metadata.get(ip, {})
                            severity = meta.get('severity', 'UNKNOWN')
                            threat = meta.get('threat_type', 'Unknown')
                            
                            sev_icon = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
                            st.markdown(f"{sev_icon} **{i}.** `{ip}` — **{severity}** ({threat})")
                    else:
                        st.success("✅ Firewall is clean. No IPs currently blocked.")
                
                with t2:
                    st.markdown("### 🔍 RECENT NETWORK ACTIVITY")
                    recent_df = df.tail(25).iloc[::-1]
                    st.dataframe(recent_df, use_container_width=True, hide_index=True)
                
                with t3:
                    st.markdown("### ⏱️ AUTO-UNBLOCK SCHEDULE")
                    if blocked_metadata:
                        st.markdown("""
                        <div style="background: rgba(0,40,0,0.5); padding: 15px; border-radius: 8px; border: 1px solid rgba(0,255,65,0.3);">
                        <b>Duration Policy:</b><br>
                        🟢 LOW: 30 min | 🟡 MEDIUM: 2 hours | 🟠 HIGH: 24 hours | 🔴 CRITICAL: Permanent
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write("")
                        for ip, data in blocked_metadata.items():
                            duration = data.get('duration_minutes', 0)
                            if duration > 0:
                                blocked_time = datetime.fromisoformat(data['blocked_at'])
                                expiry = blocked_time + timedelta(minutes=duration)
                                remaining = expiry - datetime.now()
                                
                                if remaining.total_seconds() > 0:
                                    mins_left = int(remaining.total_seconds() / 60)
                                    st.markdown(f"⏳ `{ip}` — Unblocks in **{mins_left} minutes** ({data['severity']})")
                                else:
                                    st.markdown(f"⌛ `{ip}` — **Expired** (pending removal)")
                            else:
                                st.markdown(f"🔒 `{ip}` — **PERMANENT BLOCK** ({data['severity']})")
                    else:
                        st.info("No auto-unblock schedule active. Using v1.0 backend or no blocks with metadata.")

            except Exception as e:
                st.error(f"⚠️ Dashboard Error: {str(e)}")
        else:
            st.warning("⏳ WAITING FOR BACKEND TO START...")
            st.info("Checking for: deepguard_logs.db")
    time.sleep(2)
    
    # Trigger Streamlit fragment refresh / full rerun
    st.rerun()