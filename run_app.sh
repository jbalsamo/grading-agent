#!/bin/bash
# Run the StreamLit app with the virtual environment
# Usage: ./run_app.sh [-D|--debug]

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment and run streamlit
cd "$SCRIPT_DIR"
source .venv/bin/activate

# Pass all arguments to the app (e.g., -D or --debug)
streamlit run app.py -- "$@"
