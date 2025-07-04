import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
from collections import Counter
import tempfile
import os
import base64
from io import BytesIO
from PIL import Image

# Set page config
st.set_page_config(page_title="KG Genie: Clinical Trials Explorer", layout="wide", page_icon="🧠")

# Title and description
st.title("🧠 KG Genie: Clinical Trials Knowledge Graph Explorer")
st.markdown("""
Explore relationships between clinical trials, drugs, conditions, and outcomes through an interactive knowledge graph.
""")

# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("tnbc_kg_triplets_chemical_biotech_other.csv")
        # Standardize column names if needed
        df.columns = df.columns.str.lower()
        if 'relation' not in df.columns and 'edge' in df.columns:
            df = df.rename(columns={'edge': 'relation'})
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'tnbc_kg_triplets_chemical_biotech_other.csv' is in the correct directory.")
        return pd.DataFrame()

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Exploration Controls")

# Visualization type selector
viz_type = st.sidebar.radio(
    "Visualization Type",
    ["Plotly Interactive", "PyVis Network"],
    help="Choose between different visualization engines"
)

# Node filtering
filter_type = st.sidebar.radio(
    "Explore by:",
    ["Clinical Trial", "Drug", "Condition", "Outcome"],
    help="Start your exploration from different entity types"
)

# Get unique values for each entity type
if not df.empty:
    clinical_trials = sorted(df[df['source'].str.contains('NCT', na=False)]['source'].unique())
    drugs = sorted(df[~df['source'].str.contains('NCT', na=False)]['source'].unique())
    conditions = sorted(df[df['relation'].str.contains('condition', case=False, na=False)]['target'].unique())
    outcomes = sorted(df[df['relation'].str.contains('outcome', case=False, na=False)]['target'].unique())

    selected = None
    if filter_type == "Clinical Trial":
        selected = st.sidebar.selectbox("Select Clinical Trial", ["All"] + clinical_trials)
    elif filter_type == "Drug":
        selected = st.sidebar.selectbox("Select Drug", ["All"] + drugs)
    elif filter_type == "Condition":
        selected = st.sidebar.selectbox("Select Condition", ["All"] + conditions)
    elif filter_type == "Outcome":
        selected = st.sidebar.selectbox("Select Outcome", ["All"] + outcomes)

# Max nodes slider
max_nodes = st.sidebar.slider(
    "Maximum nodes to display", 
    20, 500, 100,
    help="Limit the number of nodes for better performance"
)

# Build the filtered graph
def build_filtered_graph(selected, filter_type, max_nodes):
    G = nx.DiGraph()
    
    if selected == "All" or selected is None:
        # Sample the dataframe if it's too large
        sample_df = df.sample(min(len(df), 1000))
        for _, row in sample_df.iterrows():
            G.add_edge(row['source'], row['target'], relation=row['relation'])
    else:
        # Step 1: Direct relationships
        if filter_type == "Clinical Trial":
            direct_df = df[df['source'] == selected]
        elif filter_type == "Drug":
            direct_df = df[df['source'] == selected]
        elif filter_type == "Condition":
            direct_df = df[df['target'] == selected]
        elif filter_type == "Outcome":
            direct_df = df[df['target'] == selected]
        
        # Step 2: First-level connections
        connected_entities = set(direct_df['target'].tolist() + direct_df['source'].tolist())
        connected_df = df[
            (df['source'].isin(connected_entities)) | 
            (df['target'].isin(connected_entities))
        ]
        
        # Combine and limit size
        combined_df = pd.concat([direct_df, connected_df]).drop_duplicates()
        if len(combined_df) > max_nodes:
            combined_df = combined_df.sample(max_nodes)
        
        for _, row in combined_df.iterrows():
            G.add_edge(row['source'], row['target'], relation=row['relation'])
    
    return G

if not df.empty:
    G = build_filtered_graph(selected, filter_type, max_nodes)
else:
    G = nx.DiGraph()

# Main display area
tab1, tab2, tab3 = st.tabs(["📊 Visualization", "📋 Data Table", "📈 Statistics"])

with tab1:
    if viz_type == "Plotly Interactive":
        # Create Plotly visualization
        pos = nx.spring_layout(G, k=0.5, seed=42)
        
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
        
        node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            
            if 'NCT' in node:
                node_color.append('#1f77b4')  # Blue for clinical trials
                node_size.append(20)
            elif node in drugs:
                node_color.append('#ff7f0e')  # Orange for drugs
                node_size.append(25)
            elif node in conditions:
                node_color.append('#2ca02c')  # Green for conditions
                node_size.append(22)
            elif node in outcomes:
                node_color.append('#9467bd')  # Purple for outcomes
                node_size.append(18)
            else:
                node_color.append('#d62728')  # Red for others
                node_size.append(15)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            marker=dict(
                color=node_color,
                size=node_size,
                line=dict(width=2, color='DarkSlateGrey')
            ),
            hoverinfo='text'
        )
        
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=f"Knowledge Graph: {selected if selected != 'All' else 'Full Network'}",
                title_x=0.5,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=700
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:  # PyVis Network
        net = Network(height="700px", width="100%", directed=True, notebook=False)
        
        # Add nodes with different properties based on type
        for node in G.nodes():
            if 'NCT' in node:
                net.add_node(node, color='#1f77b4', size=20, title=node, group="clinical_trial")
            elif node in drugs:
                net.add_node(node, color='#ff7f0e', size=25, title=node, group="drug")
            elif node in conditions:
                net.add_node(node, color='#2ca02c', size=22, title=node, group="condition")
            elif node in outcomes:
                net.add_node(node, color='#9467bd', size=18, title=node, group="outcome")
            else:
                net.add_node(node, color='#d62728', size=15, title=node, group="other")
        
        # Add edges
        for edge in G.edges(data=True):
            net.add_edge(edge[0], edge[1], title=edge[2]['relation'])
        
        # Save and display
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
                net.save_graph(tmpfile.name)
                html_content = open(tmpfile.name, 'r', encoding='utf-8').read()
                st.components.v1.html(html_content, height=700, scrolling=True)
        finally:
            if 'tmpfile' in locals():
                os.unlink(tmpfile.name)

with tab2:
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No data available to display.")

with tab3:
    if not G.nodes():
        st.warning("No graph data to analyze.")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nodes", G.number_of_nodes())
            st.metric("Edges", G.number_of_edges())
            
        with col2:
            st.write("**Node Types**")
            node_types = {
                "Clinical Trials": len([n for n in G.nodes() if 'NCT' in n]),
                "Drugs": len([n for n in G.nodes() if n in drugs]),
                "Conditions": len([n for n in G.nodes() if n in conditions]),
                "Outcomes": len([n for n in G.nodes() if n in outcomes]),
                "Other": len(G.nodes()) - len([n for n in G.nodes() if 'NCT' in n or n in drugs or n in conditions or n in outcomes])
            }
            st.dataframe(pd.DataFrame.from_dict(node_types, orient='index', columns=['Count']), height=200)
            
        with col3:
            st.write("**Top Relationships**")
            relations = Counter([d['relation'] for _, _, d in G.edges(data=True)])
            st.dataframe(pd.DataFrame.from_dict(relations, orient='index', columns=['Count']), height=200)

# Image export functionality (separate section)
st.sidebar.markdown("---")
st.sidebar.header("💾 Export Options")

if st.sidebar.button("📸 Export Current View as Image"):
    if viz_type == "Plotly Interactive":
        # For Plotly, we can export directly
        img_bytes = fig.to_image(format="png")
        st.sidebar.download_button(
            label="⬇️ Download Image",
            data=img_bytes,
            file_name="knowledge_graph.png",
            mime="image/png"
        )
    else:
        # For PyVis, we'd need to use a screenshot tool
        st.sidebar.warning("For PyVis visualization, please use your browser's screenshot functionality (Ctrl+Shift+S or Cmd+Shift+S)")

# Footer
st.markdown("---")
st.markdown("""
**About KG Genie**: This interactive explorer helps visualize relationships in clinical trial data. 
Use the filters to explore specific entities and their connections.
""")