# DEEPGUARD 🛡️
**An Intelligent Intrusion Detection and Prevention System Using Random Forest**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange)
![Cybersecurity](https://img.shields.io/badge/Domain-Cybersecurity-red)
![Status](https://img.shields.io/badge/Status-Active%20Development-success)

## 📌 Overview
**DEEPGUARD** is an advanced Intrusion Detection and Prevention System (IDPS) designed to analyze network traffic and identify malicious activities with high accuracy. Leveraging a **Random Forest** machine learning classifier, this system moves beyond traditional signature-based detection to intelligently classify zero-day threats, anomalies, and known attack vectors in real-time network environments.

## ✨ Key Features
* **Intelligent Threat Detection:** Utilizes a Random Forest ensemble learning algorithm for robust, high-accuracy classification of network packets.
* **Feature Extraction & Processing:** Efficiently handles large network datasets (using Pandas and NumPy) to extract relevant features for model training and inference.
* **Interactive Dashboard:** Includes a dynamic, user-friendly visualization interface (built with Streamlit) to monitor network traffic, view threat alerts, and analyze model performance metrics.
* **Low False-Positive Rate:** Optimized hyperparameters to ensure legitimate traffic is not mistakenly dropped or flagged.

## 🛠️ Tech Stack
* **Language:** Python
* **Machine Learning:** Scikit-Learn (Random Forest Classifier)
* **Data Processing & Analysis:** Pandas, NumPy
* **Data Visualization & UI:** Matplotlib, Streamlit
* **Networking/Security Tools:** Integration with standard packet capture (PCAP) parsing libraries.

## 📂 Project Structure
```text
DEEPGUARD/
├── data/                   # Raw and processed datasets (e.g., NSL-KDD, CICIDS)
├── models/                 # Saved/Pickled Random Forest models
├── src/                    # Source code for data preprocessing and model training
│   ├── preprocess.py       # Data cleaning and feature engineering
│   ├── train.py            # Random Forest training script
│   └── predict.py          # Real-time inference engine
├── dashboard/              # Streamlit application files
│   └── app.py              # Main dashboard script
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
