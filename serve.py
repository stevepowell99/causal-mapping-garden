#!/usr/bin/env python3
"""
Simple HTTP server to serve the generated site.
Run this after building the site to avoid CORS issues.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import sys

def serve_site(site_dir="site", port=8000):
    site_path = Path(site_dir)
    if not site_path.exists():
        print(f"Site directory '{site_dir}' doesn't exist. Run build_static_site.py first.")
        return
    
    # Change to site directory
    import os
    os.chdir(site_path)
    
    # Start server
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"Serving site at {url}")
        print("Press Ctrl+C to stop")
        
        # Open browser
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    serve_site(port=port)
