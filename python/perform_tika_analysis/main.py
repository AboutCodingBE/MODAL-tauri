#!/usr/bin/env python3
import sys
import os
import json

# Ensure we can find shared and tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.tika_repository import TikaRepository
from perform_tika_analysis.perform_tika_analysis import TikaAnalysisService

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "modaldb",
    "user": "user",
    "password": "password"
}

def main():
    print("TEST")
    if len(sys.argv) < 2:
        print("Usage: python main.py <archive_id>")
        sys.exit(1)

    archive_id = sys.argv[1]
    
    try:
        # Initialize components
        repo = TikaRepository(DB_CONFIG)
        service = TikaAnalysisService(repo)
        
        # Execute analysis and get results
        results = service.run(archive_id)
        
        # Output result as JSON for Tauri
        print(json.dumps(results))

    except Exception as e:
        error_output = {"error": str(e)}
        print(json.dumps(error_output), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()