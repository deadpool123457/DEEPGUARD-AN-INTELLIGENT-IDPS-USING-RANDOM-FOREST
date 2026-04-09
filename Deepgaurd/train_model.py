import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

print("--- DEEPGAURD BRAIN TRAINING ---")

# 1. CHECK FOR DATA
if not os.path.exists('KDDTrain+.txt'):
    print("[ERROR] 'KDDTrain+.txt' not found. Did you run the download script?")
    exit()

print("Loading Dataset... (This takes a moment)")
columns = ["duration","protocol_type","service","flag","src_bytes","dst_bytes","land",
           "wrong_fragment","urgent","hot","num_failed_logins","logged_in",
           "num_compromised","root_shell","su_attempted","num_root","num_file_creations",
           "num_shells","num_access_files","num_outbound_cmds","is_host_login",
           "is_guest_login","count","srv_count","serror_rate","srv_serror_rate",
           "rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate",
           "srv_diff_host_rate","dst_host_count","dst_host_srv_count",
           "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
           "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
           "dst_host_rerror_rate","dst_host_srv_rerror_rate","label", "difficulty"]

df = pd.read_csv('KDDTrain+.txt', names=columns)

# 2. SELECT FEATURES
# We use Random Forest to analyze Protocol, Service, and Packet Size
X = df[['protocol_type', 'service', 'src_bytes']]
y = df['label'].apply(lambda x: 0 if x == 'normal' else 1) # 0=Safe, 1=Attack

# 3. ENCODE
p_encoder = LabelEncoder()
s_encoder = LabelEncoder()
X.loc[:, 'protocol_type'] = p_encoder.fit_transform(X['protocol_type'])
X.loc[:, 'service'] = s_encoder.fit_transform(X['service'])

# 4. TRAIN
print("Training Random Forest Model (100 Trees)...")
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# 5. SAVE BRAIN & REPORT DATA
importance = rf_model.feature_importances_
feature_names = ['Protocol', 'Service', 'Packet Size']

data = {
    'model': rf_model, 
    'pe': p_encoder, 
    'se': s_encoder,
    'importance': importance,
    'feature_names': feature_names
}
joblib.dump(data, 'deepgaurd_brain.pkl')
print("\n[SUCCESS] AI Brain saved as 'deepgaurd_brain.pkl'")