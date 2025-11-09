import sys
from pathlib import Path

from src.gmail_worker.poller import run_poller

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.BackEnd.app import create_app

if __name__ == "__main__":
    run_poller()
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5001)
