#!/bin/bash

# Check if content directory exists in the repository
if [ -d "content" ]; then
    echo "Using content directory from repository"
    python build_static_site.py --input ./content --output ./site --title "Causal Mapping"
else
    echo "Error: No content directory found."
    echo "Please add your Obsidian vault content to a 'content' directory in the repository."
    exit 1
fi
