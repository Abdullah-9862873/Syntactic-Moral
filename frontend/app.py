"""
Syntactic Morality Analyzer - Frontend
"""

import streamlit as st
import sys
import json
from pathlib import Path

# CRITICAL: Set up paths based on where Streamlit is running from
# Streamlit runs from its own directory, not the project root

# Get the app.py directory
THIS_FILE = Path(__file__).resolve()
FRONTEND_DIR = THIS_FILE.parent          # .../SyntacticMoral/frontend/
PROJECT_ROOT = FRONTEND_DIR.parent       # .../SyntacticMoral/
BACKEND_DIR = PROJECT_ROOT / "backend"
PIPELINE_DIR = BACKEND_DIR / "pipeline"

# Clear any existing bad paths and add correct ones
# Remove duplicates and move our paths to front
new_path = [str(PROJECT_ROOT), str(BACKEND_DIR), str(PIPELINE_DIR)]
for p in new_path:
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

# Force reload to clear any cached bad imports
import importlib
for mod_name in ['backend', 'backend.pipeline',
                 'backend.pipeline.dictionaries',
                 'backend.pipeline.parser',
                 'backend.pipeline.scorer',
                 'dictionaries', 'scorer']:
    if mod_name in sys.modules:
        del sys.modules[mod_name]

# Page config
st.set_page_config(
    page_title="Syntactic Morality Analyzer",
    page_icon="X",
    layout="wide"
)

def import_pipeline_module(module_filename, module_name):
    """Import a pipeline module by file path to avoid shadowing builtins."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        module_name, str(PIPELINE_DIR / module_filename)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def init_components():
    """Initialize the pipeline components."""
    dicts_mod  = import_pipeline_module("dictionaries.py",    "pipeline_dictionaries")
    parser_mod = import_pipeline_module("syntactic_parser.py", "pipeline_parser")
    scorer_mod = import_pipeline_module("scorer.py",           "pipeline_scorer")

    DictionaryLoader = dicts_mod.DictionaryLoader
    SyntacticParser  = parser_mod.SyntacticParser
    MoralScorer      = scorer_mod.MoralScorer

    dict_loader = DictionaryLoader(str(BACKEND_DIR / "data"))
    dict_loader.load_all()

    parser = SyntacticParser()
    scorer = MoralScorer(dict_loader, parser)

    return dict_loader, parser, scorer

def load_results():
    """Load training results from models folder."""
    results_file = BACKEND_DIR / "models" / "multi_dict_results.json"
    if results_file.exists():
        with open(results_file) as f:
            return json.load(f)
    return None

@st.cache_resource
def load_components():
    return init_components()

def main():
    """Main app function."""
    # Initialize loading message with progress bar
    progress_bar = st.progress(0, text="Loading models and dictionaries...")
    progress_bar.progress(30, text="Loading dictionaries...")
    
    # Initialize components
    dict_loader, parser, scorer = load_components()
    
    progress_bar.progress(70, text="Loading parser...")
    
    progress_bar.progress(100, text="Ready!")
    progress_bar.empty()
    
    # App title and description
    st.title("Syntactic Morality Analyzer")
    st.markdown("**Extension to eMACDscore** (Malik et al., 2025)")
    st.markdown("Adds syntactic weighting to detect negation and grammatical roles.")
    
    # Sidebar with dictionary selection
    st.sidebar.header("Settings")
    dict_options = {
        "mfd": "MFD", 
        "mfd2": "MFD 2.0", 
        "emfd": "eMFD", 
        "emacd": "eMACD", 
        "macd": "MACD"
    }
    selected_dict = st.sidebar.selectbox(
        "Dictionary", 
        list(dict_options.keys()),
        format_func=lambda x: dict_options[x]
    )
    
    # Show training results in sidebar
    results = load_results()
    if results:
        st.sidebar.markdown("### Training Results (Macro F1)")
        for d, r in results.items():
            b = round(r.get("baseline", {}).get("macro", 0), 3)
            s = round(r.get("syntax", {}).get("macro", 0), 3)
            diff = round(s - b, 3)
            st.sidebar.markdown(f"**{d}**: {b} -> {s} ({diff:+})")
    
    # Text input
    st.header("Input Text")
    text_input = st.text_area(
        "Enter text to analyze:", 
        height=80, 
        placeholder="e.g., I'm not caring about fairness"
    )
    
    # Analysis buttons
    col1, col2 = st.columns(2)
    with col1:
        analyze_synx = st.button("Analyze with Syntax", type="primary", use_container_width=True)
    with col2:
        analyze_baseline = st.button("Analyze Baseline", use_container_width=True)
    
    # Display results
    if text_input and (analyze_synx or analyze_baseline):
        progress_bar = st.progress(0, text="Loading scorer...")
        progress_bar.progress(25, text="Analyzing text...")
        
        baseline_scores = scorer.score_baseline(text_input, selected_dict)
        
        progress_bar.progress(50, text="Computing baseline scores...")
        
        syntax_scores = scorer.score(text_input, selected_dict)
        
        progress_bar.progress(100, text="Done!")
        progress_bar.empty()
        
        st.divider()
        st.header("Results")
        
        if analyze_baseline:
            st.subheader("Baseline (Keyword Only)")
            for domain, score in baseline_scores.items():
                if score > 0:
                    st.progress(float(score), text=f"{domain}: {score:.3f}")
        
        if analyze_synx:
            st.subheader("Syntax-Enhanced")
            for domain, score in syntax_scores.items():
                if score > 0:
                    delta = score - baseline_scores.get(domain, 0)
                    st.progress(float(score), text=f"{domain}: {score:.3f} ({delta:+.3f})")
            
            # Syntactic breakdown
            st.subheader("Syntactic Breakdown")
            syntactic = parser.parse(text_input)
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Tokens:**", syntactic["tokens"])
                st.write("**Subjects:**", [s["text"] for s in syntactic.get("subjects", [])])
            with col2:
                st.write("**Objects:**", [o["text"] for o in syntactic.get("objects", [])])
            
            if syntactic.get("negation_scopes"):
                st.warning("Negation detected! Keywords in negation scope have reduced scores.")

if __name__ == "__main__":
    main()