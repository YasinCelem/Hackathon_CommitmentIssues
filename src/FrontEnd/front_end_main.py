import sys
from pathlib import Path
from threading import Thread

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.FrontEnd import create_app

# Create app instance for Flask CLI
app = create_app()

# Try to import Gmail worker (optional - only if dependencies are installed)
try:
    from src.gmail_worker.poller import run_poller
    GMAIL_WORKER_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Gmail worker not available: {e}")
    print("[INFO] Frontend will run without Gmail worker functionality")
    GMAIL_WORKER_AVAILABLE = False
    run_poller = None


if __name__ == "__main__":
    # Start poller in background thread (if available)
    if GMAIL_WORKER_AVAILABLE and run_poller:
        try:
            poller_thread = Thread(target=run_poller, args=(app,), daemon=True)
            poller_thread.start()
            print("[INFO] Gmail worker started in background thread")
        except Exception as e:
            print(f"[WARN] Failed to start Gmail worker: {e}")
            print("[INFO] Frontend will continue without Gmail worker")

    # Run Flask app (blocking)
    app.run(debug=True, host="0.0.0.0", port=5000)
