# Syntactic Morality Analyzer
# Launcher script that properly sets up Python paths

import os
import sys
from pathlib import Path

# Get project root (parent of frontend)
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
PIPELINE_DIR = BACKEND_DIR / "pipeline"

# Add to Python path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(PIPELINE_DIR))

# Change to project directory for relative paths
os.chdir(PROJECT_ROOT)

# Now run Streamlit
from streamlit.web import cli as stcli
import sys

sys.argv = ["streamlit", "run", "frontend/app.py"]

if __name__ == "__main__":
    stcli.main()