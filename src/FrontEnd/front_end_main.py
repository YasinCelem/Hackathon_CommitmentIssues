import sys
from pathlib import Path
from threading import Thread

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.FrontEnd import create_app
from src.gmail_worker.poller import run_poller


if __name__ == "__main__":
    app = create_app()

    # Start poller in background thread
    poller_thread = Thread(target=run_poller, args=(app,), daemon=True)
    poller_thread.start()

    # Run Flask app (blocking)
    app.run(debug=True, host="0.0.0.0", port=5000)
