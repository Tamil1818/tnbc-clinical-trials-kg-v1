# 🧬 TNBC Clinical Trials Knowledge Graph (v1)

This app is a subunit of the larger TNBC Knowledge Graph (KG Genie) project. It allows users to explore biotech and chemical drugs in clinical trials, including biomarkers and relationships through an interactive knowledge graph.

## 🔍 Features
- Clinical trials filtered by biotech/chemical/other drugs
- Biomarker & pathway extraction
- Graph relationships: trial–drug–biomarker–outcome
- Interactive visualizations with PyVis and Plotly
- CSV export + image download support
🔗 Live App: [Click to launch](https://tnbc-clinical-trials-kg-v1.streamlit.app)
📁 Dataset: Included `tnbc_kg_triplets_chemical_biotech_other.csv`

## 📁 Files
- `tnbc_clean.py` — Streamlit app
- `tnbc_kg_triplets_chemical_biotech_other.csv` — Data used in the graph
- `requirements.txt` — Python dependencies

## 📊 Example Triplet Format
| Source         | Relation       | Target      |
|----------------|----------------|-------------|
| BIOTECH_TRIAL:NCT123456 | TARGETS_PROTEIN | BRCA1       |
| CHEMICAL_TRIAL:NCT654321 | MEASURES        | Response Rate |

## 🛠 How to Run Locally

```bash
git clone https://github.com/YourUser/tnbc-clinical-trial-subunit-app.git
cd tnbc-clinical-trial-subunit-app
pip install -r requirements.txt
streamlit run tnbc_clean.py
