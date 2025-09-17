#!/usr/bin/env python3
"""
Simple search page generator.
Just creates a working search.html with no template complexity.
"""

from pathlib import Path
import json
import re

def create_search_page(output_root: Path):
    # Read the search index
    index_path = output_root / "assets" / "search_index.json"
    if not index_path.exists():
        print("No search index found!")
        return
    
    search_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Search</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 2rem; }
        .result { margin-bottom: 1rem; }
        .result .title { font-weight: 600; display: block; }
        .result .snippet { color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Search</h1>
        <form id="searchForm" class="mb-3">
            <div class="input-group">
                <input type="text" id="searchInput" class="form-control" placeholder="Search...">
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>
        <div id="results"></div>
    </div>
    
    <script>
        let searchIndex = [];
        
        // Load search index
        fetch('./assets/search_index.json')
            .then(response => response.json())
            .then(data => {
                searchIndex = data;
                performSearch();
            });
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function performSearch() {
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const resultsDiv = document.getElementById('results');
            
            if (!query) {
                resultsDiv.innerHTML = '';
                return;
            }
            
            const results = searchIndex.filter(item => {
                const searchText = (item.title + ' ' + item.text).toLowerCase();
                return searchText.includes(query);
            });
            
            if (results.length === 0) {
                resultsDiv.innerHTML = '<p class="text-muted">No results found.</p>';
                return;
            }
            
            let html = '';
            results.slice(0, 20).forEach(item => {
                const textLower = item.text.toLowerCase();
                const queryPos = textLower.indexOf(query);
                let snippet = item.text;
                
                if (queryPos >= 0) {
                    const start = Math.max(0, queryPos - 50);
                    const end = Math.min(item.text.length, queryPos + 150);
                    snippet = item.text.substring(start, end);
                    if (start > 0) snippet = '...' + snippet;
                    if (end < item.text.length) snippet = snippet + '...';
                }
                
                html += `<div class="result">
                    <a href="${item.path}" class="title">${escapeHtml(item.title)}</a>
                    <div class="snippet">${escapeHtml(snippet)}</div>
                </div>`;
            });
            
            resultsDiv.innerHTML = html;
        }
        
        // Get query from URL and populate search box
        const urlParams = new URLSearchParams(window.location.search);
        const initialQuery = urlParams.get('q') || '';
        document.getElementById('searchInput').value = initialQuery;
        
        // Search on form submit
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            performSearch();
        });
        
        // Search on input
        document.getElementById('searchInput').addEventListener('input', performSearch);
    </script>
</body>
</html>"""
    
    (output_root / "search.html").write_text(search_html, encoding="utf-8")
    print("Created simple search.html")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        output_path = Path("./site")
    
    create_search_page(output_path)
