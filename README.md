# 🧠 TNBC Clinical Trials Explorer (Knowledge Graph Subunit)

This is an interactive **Streamlit application** for exploring clinical trials related to **Triple-Negative Breast Cancer (TNBC)** using **Knowledge Graph (KG)** visualizations.

It is designed as a **modular subunit** for the larger [TNBC KG platform](https://kg-genie-ai-powered-knowledge-graph-for-cancer-research-evzhhj.streamlit.app/), and can be used standalone or integrated into more complex biomedical KG systems.

---

## 🚀 Features

- 📊 Visualizes clinical trial relationships (biotech, chemical, other drugs)
- 🧬 Extracts drug-target-biomarker-pathway relationships
- 🧠 Displays knowledge graphs (Plotly + PyVis)
- 📁 Categorizes drugs: Biotech, Chemical, Other
- 🔍 Filters trials by drug type, biomarker, relation
- 📦 Export graph views or data

---

## 📂 Files in This Repo

| File | Description |
|------|-------------|
| `tnbc_clean.py` | Main Streamlit app |
| `tnbc_kg_triplets_chemical_biotech_other.csv` | Processed KG triplets from TNBC trial data |
| `requirements.txt` | Python libraries needed to run the app |
| `README.md` | This file |

---

## ▶️ How to Run Locally

```bash
# Step 1: Clone the repo
git clone https://github.com/your-username/tnbc-kg-app.git
cd tnbc-kg-app

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run the Streamlit app
streamlit run tnbc_clean.py
