"""
Syntactic Morality Analyzer - Streamlit Web Application
Run with: streamlit run app.py
"""

import streamlit as st
import sys
import json
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent

# For local: SyntacticMoral/ contains backend/
# For HF Space: app.py is at root, backend/ is at root too
if (PROJECT_ROOT / "backend").exists():
    BACKEND_DIR = PROJECT_ROOT / "backend"
else:
    # HF Space structure - backend is at same level as app.py
    BACKEND_DIR = THIS_FILE.parent / "backend"
    if not BACKEND_DIR.exists():
        BACKEND_DIR = THIS_FILE.parent

PIPELINE_DIR = BACKEND_DIR / "pipeline"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))
if PIPELINE_DIR.exists():
    sys.path.insert(0, str(PIPELINE_DIR))

import importlib
for mod in ['dictionaries', 'scorer', 'syntactic_parser', 'parser']:
    if mod in sys.modules:
        del sys.modules[mod]

from backend.pipeline.dictionaries import DictionaryLoader
from backend.pipeline.parser import SyntacticParser
from backend.pipeline.scorer import MoralScorer

st.set_page_config(page_title="Syntactic Morality Analyzer", page_icon="X", layout="wide")

@st.cache_resource
def load_components():
    dict_loader = DictionaryLoader(str(BACKEND_DIR / "data"))
    dict_loader.load_all()
    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)
    return dict_loader, parser, scorer

def main():
    st.title("Syntactic Morality Analyzer")
    st.markdown("**Extension to eMACD** (Malik et al., 2025) - Adds syntactic weighting")
    
    dict_loader, parser, scorer = load_components()
    
    dict_options = {"mfd": "MFD", "mfd2": "MFD 2.0", "emfd": "eMFD", "emacd": "eMACD", "macd": "MACD"}
    selected_dict = st.sidebar.selectbox("Dictionary", list(dict_options.keys()), format_func=lambda x: dict_options[x])
    
    text_input = st.text_area("Enter text to analyze:", height=80, placeholder="e.g., I care about fairness")
    
    col1, col2 = st.columns(2)
    with col1:
        analyze_synx = st.button("Analyze with Syntax", type="primary", use_container_width=True)
    with col2:
        analyze_baseline = st.button("Analyze Baseline", use_container_width=True)
    
    if text_input and (analyze_synx or analyze_baseline):
        st.divider()
        st.header("Results")
        
        baseline_scores = scorer.score_baseline(text_input, selected_dict)
        syntax_scores = scorer.score(text_input, selected_dict)
        domains = dict_loader.get_domains(selected_dict)
        
        if analyze_baseline:
            st.subheader("Baseline (Keyword Only)")
            for domain, score in baseline_scores.items():
                if score > 0:
                    st.progress(float(score), text=f"{domain}: {score:.3f}")
        
        if analyze_synx:
            st.subheader("Syntax-Enhanced Results")
            for domain in domains:
                score = syntax_scores.get(domain, 0)
                delta = score - baseline_scores.get(domain, 0)
                st.progress(float(score), text=f"{domain}: {score:.3f} ({delta:+.3f})")
        
        st.subheader("Syntactic Breakdown")
        syntactic = parser.parse(text_input)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Tokens:**", syntactic["tokens"])
        with col2:
            st.write("**Subjects:**", [s["text"] for s in syntactic.get("subjects", [])])
        with col3:
            st.write("**Objects:**", [o["text"] for o in syntactic.get("objects", [])])

if __name__ == "__main__":
    main()