"""pipeline/run_daily_v2.py — Automation V3 Master Entrypoint.

Refactored: Delegates directly to arcade_orchestrator.py.
Retires legacy 4K long-form + 5 slop-shorts generator in favor of the
autonomous, $0-cost, anti-slop Arcade Motion Graphics engine.
"""
import sys
from pathlib import Path

# Forward all arguments directly to arcade_orchestrator
from arcade_orchestrator import main

if __name__ == "__main__":
    main()
