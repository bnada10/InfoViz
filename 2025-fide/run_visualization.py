#!/usr/bin/env python3
"""
Chess Player Rating Analysis Visualization - One-Click Launcher
This script starts a local server and opens the visualization in your default browser.
"""

import os
import sys
import webbrowser
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Suppress default logging"""
    def log_message(self, format, *args):
        pass

def find_free_port(start_port=8000):
    """Find an available port"""
    port = start_port
    while port < 8100:
        try:
            server = HTTPServer(('localhost', port), QuietHTTPRequestHandler)
            server.server_close()
            return port
        except OSError:
            port += 1
    return None

def main():
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Verify data file exists
    data_file = script_dir / 'viz' / 'chess_data_aggregated.json'
    if not data_file.exists():
        print("Error: chess_data_aggregated.json not found in viz/ directory")
        print("Please ensure the data file is in the correct location.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Find available port
    port = find_free_port()
    if port is None:
        print("Error: Could not find an available port")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Start server
    handler = QuietHTTPRequestHandler
    server = HTTPServer(('localhost', port), handler)
    
    url = f'http://localhost:{port}/viz/chess_visualization.html'
    
    print("=" * 60)
    print(" Chess Player Rating Analysis Visualization")
    print("=" * 60)
    print(f" Server running on: {url}")
    print(f" Opening in browser...")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser
    webbrowser.open(url)
    
    # Start server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n Server stopped")
        server.server_close()
        sys.exit(0)

if __name__ == '__main__':
    main()
