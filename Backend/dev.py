"""Dev server runner with auto-restart on crash.

Wraps uvicorn --reload so that if the server process crashes
(common on Windows due to signal handling issues), it automatically
restarts after a short delay.

Usage:
    python dev.py
"""

import subprocess
import sys
import time
from datetime import datetime

CMD = [
    sys.executable, "-m", "uvicorn",
    "app.main:app",
    "--reload",
    "--host", "0.0.0.0",
    "--port", "8000",
]

RESTART_DELAY = 1  # seconds
MAX_RAPID_CRASHES = 5  # max crashes within RAPID_WINDOW before slowing down
RAPID_WINDOW = 10  # seconds
SLOW_DELAY = 5  # seconds — delay when crashing too fast


def main() -> None:
    crash_times: list[float] = []

    while True:
        now = time.time()
        print(
            f"\n[dev] Starting uvicorn... ({datetime.now().strftime('%H:%M:%S')})",
            flush=True,
        )
        try:
            result = subprocess.run(CMD)
            exit_code = result.returncode
        except KeyboardInterrupt:
            print("\n[dev] Stopped by user", flush=True)
            break

        if exit_code == 0:
            print("[dev] Server stopped cleanly", flush=True)
            break

        # Track crash frequency
        crash_times.append(time.time())
        # Keep only crashes within the window
        crash_times = [t for t in crash_times if time.time() - t < RAPID_WINDOW]

        if len(crash_times) >= MAX_RAPID_CRASHES:
            delay = SLOW_DELAY
            print(
                f"[dev] Server crashed {len(crash_times)}x in {RAPID_WINDOW}s "
                f"(exit code {exit_code}), waiting {delay}s...",
                flush=True,
            )
        else:
            delay = RESTART_DELAY
            print(
                f"[dev] Server crashed (exit code {exit_code}), "
                f"restarting in {delay}s...",
                flush=True,
            )

        try:
            time.sleep(delay)
        except KeyboardInterrupt:
            print("\n[dev] Stopped by user", flush=True)
            break


if __name__ == "__main__":
    main()
