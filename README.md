# Obsidian Static Site Generator

A Python script that converts an Obsidian vault into a beautiful static website with:

- **Collapsible navigation**: Left sidebar with folder structure, starts narrow and expands on hover
- **Wikilink embeds**: Internal links display as collapsible content panels 
- **Search functionality**: Client-side search with highlighting
- **Table of contents**: Right sidebar for multi-heading pages
- **Academic styling**: Clean, readable design with ample whitespace

## Features

- Responsive Bootstrap 5 layout
- Obsidian-style wikilinks (`[[link]]`) rendered as embedded content
- Automatic ToC generation for pages with multiple headings
- Search with real-time filtering and highlighting
- Opacity effects and smooth transitions
- Only numbered folders included in navigation

## Usage

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate the site:
   ```bash
   python build_static_site.py --input "path/to/obsidian/vault" --output ./site --title "Site Title"
   ```

3. Serve locally:
   ```bash
   python serve.py
   ```

### Netlify Deployment

This repository is configured for automatic Netlify deployment:

1. Connect your Git repository to Netlify
2. Netlify will automatically detect the `netlify.toml` configuration
3. The build process will generate the static site in the `site/` directory
4. Update the input path in `netlify.toml` to point to your Obsidian vault

## File Structure

- `build_static_site.py` - Main site generator
- `serve.py` - Local development server  
- `netlify.toml` - Netlify build configuration
- `requirements.txt` - Python dependencies
- `site/` - Generated static site (not in repo)

## Customization

The site styling and behavior can be customized by editing the CSS and JavaScript within `build_static_site.py`.
