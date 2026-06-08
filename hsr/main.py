import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app
import callbacks.callbacks  # registers all callbacks

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  HS2 Intelligence Dashboard")
    print("  Monte Carlo · Scenario Analysis · Narrative Engine")
    print("="*60)
    print("\n  → Open http://0.0.0.0:8050 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=8050)