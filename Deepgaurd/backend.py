import time
from scapy.all import sniff, IP, TCP, UDP, ICMP
import joblib, csv, os, subprocess, random
from datetime import datetime, timedelta
import json
from collections import defaultdict
import threading
import sqlite3

file_lock = threading.RLock()

# --- CONFIGURATION ---
DB_FILE = 'deepguard_logs.db'
BLOCKED_FILE = 'blocked_ips.txt'
BLOCKED_METADATA_FILE = 'blocked_ips_metadata.json'
MODE_FILE = 'mode.txt'
WHITELIST_FILE = 'whitelist.txt'

# Whitelist of IPs that should NEVER be blocked
DEFAULT_WHITELIST = [
    '127.0.0.1',      # Localhost
    '192.168.1.1',    # Common router
    '8.8.8.8',        # Google DNS
    '8.8.4.4',        # Google DNS
    '1.1.1.1',        # Cloudflare DNS
]

# Auto-unblock configuration (in minutes)
BLOCK_DURATIONS = {
    'LOW': 30,      # Low severity: 30 minutes
    'MEDIUM': 120,  # Medium severity: 2 hours
    'HIGH': 1440,   # High severity: 24 hours
    'CRITICAL': 0   # Critical: permanent (0 = no auto-unblock)
}

# Threat detection tracking
connection_tracker = defaultdict(lambda: {'count': 0, 'first_seen': None, 'last_seen': None, 'ports': set()})
packet_rate_tracker = defaultdict(list)

# --- WHITELIST MANAGEMENT ---
def load_whitelist():
    """Load whitelist from file or create default"""
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    else:
        # Create default whitelist
        with open(WHITELIST_FILE, 'w') as f:
            for ip in DEFAULT_WHITELIST:
                f.write(f"{ip}\n")
        return DEFAULT_WHITELIST

WHITELIST = load_whitelist()

def is_whitelisted(ip):
    """Check if IP is in whitelist"""
    return ip in WHITELIST

# --- DATABASE SETUP ---
def init_db():
    with file_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT,
                Source_IP TEXT,
                Destination_IP TEXT,
                Protocol TEXT,
                Length INTEGER,
                Status TEXT,
                country TEXT,
                lat REAL,
                lon REAL,
                Severity TEXT,
                Threat_Type TEXT
            )
        ''')
        conn.commit()
        conn.close()

init_db()

# --- AUTO-UNBLOCK METADATA ---
def load_blocked_metadata():
    """Load metadata about blocked IPs (timestamps, severity, etc.)"""
    with file_lock:
        if os.path.exists(BLOCKED_METADATA_FILE):
            with open(BLOCKED_METADATA_FILE, 'r') as f:
                return json.load(f)
        return {}

def save_blocked_metadata(metadata):
    """Save metadata about blocked IPs"""
    with file_lock:
        with open(BLOCKED_METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)

def check_and_unblock_expired():
    """Check for expired blocks and auto-unblock them"""
    metadata = load_blocked_metadata()
    current_time = datetime.now()
    unblocked = []
    
    for ip, data in list(metadata.items()):
        block_duration = data.get('duration_minutes', 0)
        
        # Skip permanent blocks
        if block_duration == 0:
            continue
        
        # Check if block has expired
        blocked_time = datetime.fromisoformat(data['blocked_at'])
        expiry_time = blocked_time + timedelta(minutes=block_duration)
        
        if current_time >= expiry_time:
            # Unblock the IP
            unblock_ip(ip)
            unblocked.append(ip)
            del metadata[ip]
    
    if unblocked:
        save_blocked_metadata(metadata)
        print(f"[AUTO-UNBLOCK] Expired blocks removed: {', '.join(unblocked)}")
    
    return unblocked

def unblock_ip(ip):
    """Remove IP from firewall and blocked list"""
    # Remove from Windows firewall
    cmd = f"netsh advfirewall firewall delete rule name=\"Deepguard_Block_{ip}\""
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        print(f"[UNBLOCK] Removed firewall rule for {ip}")
    except:
        pass
    
    # Remove from blocked_ips.txt
    with file_lock:
        if os.path.exists(BLOCKED_FILE):
            with open(BLOCKED_FILE, 'r') as f:
                lines = f.readlines()
            with open(BLOCKED_FILE, 'w') as f:
                for line in lines:
                    if line.strip() != ip:
                        f.write(line)

# --- ENHANCED LOGGING ---
def log_packet(src, dst, proto, length, status, country, lat, lon, severity='LOW', threat_type='Unknown'):
    """Enhanced logging with severity and threat type"""
    timestamp = time.strftime("%H:%M:%S")
    with file_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (Timestamp, Source_IP, Destination_IP, Protocol, Length, Status, country, lat, lon, Severity, Threat_Type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, src, dst, proto, length, status, country, lat, lon, severity, threat_type))
        conn.commit()
        conn.close()

# --- ADVANCED THREAT DETECTION ---
def calculate_threat_severity(src_ip, packet_length, detection_reason):
    """Calculate threat severity based on multiple factors"""
    severity = 'LOW'
    threat_type = 'Anomaly'
    
    # Get connection history
    conn = connection_tracker[src_ip]
    
    # Factor 1: Packet size
    if packet_length > 5000:
        severity = 'HIGH'
        threat_type = 'Large Packet Attack'
    elif packet_length > 2500:
        severity = 'MEDIUM'
        threat_type = 'Suspicious Packet Size'
    
    # Factor 2: Connection frequency
    if conn['count'] > 100:
        severity = 'CRITICAL'
        threat_type = 'DDoS/Flooding'
    elif conn['count'] > 50:
        severity = 'HIGH'
        threat_type = 'High Volume Attack'
    
    # Factor 3: Port scanning detection
    if len(conn['ports']) > 10:
        severity = 'HIGH'
        threat_type = 'Port Scanning'
    
    # Factor 4: Rate limiting (packets per second)
    current_time = time.time()
    packet_rate_tracker[src_ip].append(current_time)
    # Keep only last 10 seconds of packets
    packet_rate_tracker[src_ip] = [t for t in packet_rate_tracker[src_ip] if current_time - t < 10]
    
    if len(packet_rate_tracker[src_ip]) > 100:  # More than 100 packets in 10 seconds
        severity = 'CRITICAL'
        threat_type = 'Rate Limit Exceeded'
    
    # Factor 5: AI prediction confidence (if available)
    if detection_reason == 'AI_HIGH_CONFIDENCE':
        if severity == 'LOW':
            severity = 'MEDIUM'
    
    return severity, threat_type

# --- ENHANCED BLOCKING LOGIC ---
def block_ip(ip, severity='MEDIUM', threat_type='Unknown'):
    """Block IP with severity-based duration and whitelist check"""
    
    # Check whitelist first
    if is_whitelisted(ip):
        print(f"[WHITELIST] Skipping block for whitelisted IP: {ip}")
        return
    
    # Check Mode
    mode = "ACTIVE"
    if os.path.exists(MODE_FILE):
        with open(MODE_FILE, 'r') as f: 
            mode = f.read().strip()
    
    if mode == "MONITOR":
        print(f"[MONITOR MODE] Would block {ip} (Severity: {severity}, Type: {threat_type})")
        return
    
    # Check if already blocked
    with file_lock:
        if os.path.exists(BLOCKED_FILE):
            with open(BLOCKED_FILE, 'r') as f:
                if ip in f.read(): 
                    return
        
        # Block the IP
        cmd = f"netsh advfirewall firewall add rule name=\"Deepguard_Block_{ip}\" dir=in action=block remoteip={ip}"
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            # Write to blocked file
            with open(BLOCKED_FILE, 'a') as f: 
                f.write(f"{ip}\n")
        
            # Save metadata for auto-unblock
            metadata = load_blocked_metadata()
            metadata[ip] = {
                'blocked_at': datetime.now().isoformat(),
                'severity': severity,
                'threat_type': threat_type,
                'duration_minutes': BLOCK_DURATIONS.get(severity, 120)
            }
            save_blocked_metadata(metadata)
            
            duration_text = f"{BLOCK_DURATIONS[severity]} min" if BLOCK_DURATIONS[severity] > 0 else "PERMANENT"
            print(f"[!!!] BLOCKED: {ip} | Severity: {severity} | Type: {threat_type} | Duration: {duration_text}")
        
        except Exception as e:
            print(f"[ERROR] Failed to block {ip}: {e}")

# --- LOAD AI ---
data = joblib.load('deepguard_brain.pkl')
model, pe = data['model'], data['pe']

# --- ENHANCED PACKET SNIFFER ---
def process(pkt):
    if not pkt.haslayer(IP): 
        return
    
    src, dst, length = pkt[IP].src, pkt[IP].dst, len(pkt)
    proto = 'tcp' if pkt.haslayer(TCP) else 'udp' if pkt.haslayer(UDP) else 'icmp'
    
    # Track connection patterns
    conn = connection_tracker[src]
    conn['count'] += 1
    conn['last_seen'] = time.time()
    if conn['first_seen'] is None:
        conn['first_seen'] = time.time()
    
    # Track destination ports for port scanning detection
    if pkt.haslayer(TCP):
        conn['ports'].add(pkt[TCP].dport)
    elif pkt.haslayer(UDP):
        conn['ports'].add(pkt[UDP].dport)
    
    try:
        # AI Prediction
        p_val = pe.transform([proto])[0] if proto in pe.classes_ else 0
        pred = model.predict([[p_val, 0, length]])[0]
        
        # Multi-factor threat detection
        is_threat = False
        detection_reason = 'NONE'
        
        # Check 1: AI Model
        if pred == 1:
            is_threat = True
            detection_reason = 'AI_PREDICTION'
        
        # Check 2: Large packet
        if length > 2500:
            is_threat = True
            detection_reason = 'LARGE_PACKET'
        
        # Check 3: Rate limiting
        current_time = time.time()
        packet_rate_tracker[src].append(current_time)
        packet_rate_tracker[src] = [t for t in packet_rate_tracker[src] if current_time - t < 10]
        if len(packet_rate_tracker[src]) > 100:
            is_threat = True
            detection_reason = 'RATE_LIMIT'
        
        # Check 4: Port scanning
        if len(conn['ports']) > 10:
            is_threat = True
            detection_reason = 'PORT_SCAN'
        
        if is_threat:
            # Calculate severity and threat type
            severity, threat_type = calculate_threat_severity(src, length, detection_reason)
            
            # Assign random coordinates for map visualization
            origins = [
                ("USA", 37.09, -95.71), 
                ("China", 35.86, 104.19), 
                ("Russia", 61.52, 105.31), 
                ("Brazil", -14.23, -51.92),
                ("N.Korea", 40.34, 127.51),
                ("Iran", 32.42, 53.68)
            ]
            country, lat, lon = random.choice(origins)
            
            log_packet(src, dst, proto, length, "MALICIOUS", country, lat, lon, severity, threat_type)
            block_ip(src, severity, threat_type)
        else:
            log_packet(src, dst, proto, length, "Safe", "Local", 0, 0, 'LOW', 'Normal')
            
    except Exception as e:
        print(f"[ERROR] Processing packet: {e}")

# --- MAIN LOOP ---
print("=" * 60)
print("   DEEPGUARD ENHANCED - INTELLIGENT IDPS v2.0")
print("=" * 60)
print(f"[+] Auto-Unblock: ENABLED")
print(f"[+] Whitelist: {len(WHITELIST)} protected IPs")
print(f"[+] Advanced Detection: Port Scan, Rate Limit, AI")
print(f"[+] Severity-Based Blocking: LOW(30m), MEDIUM(2h), HIGH(24h), CRITICAL(PERM)")
print("=" * 60)

# Check for expired blocks on startup
check_and_unblock_expired()

# Start background thread for periodic unblock checks
def periodic_unblock_check():
    while True:
        time.sleep(60)  # Check every minute
        check_and_unblock_expired()

unblock_thread = threading.Thread(target=periodic_unblock_check, daemon=True)
unblock_thread.start()

print("\n[ACTIVE] Monitoring network traffic...")
sniff(prn=process, store=0)