#!/usr/bin/env python3
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tika_repository import TikaRepository
from perform_tika_analysis import PerformTikaAnalysis


def main() -> None:
    if len(sys.argv) != 2:
        print("Gebruik: main.py <uuid van archief>")
        sys.exit(1)

    archiveuuid = sys.argv[1]
    
    try:
        error = PerformTikaAnalysis().execute(archiveuuid)
    except Exception as e:
        print(f"Onverwachte fout: {e}")
        sys.exit(1)

    if error is not None:
        print(error)
        sys.exit(1)

if __name__ == "__main__":
    main()