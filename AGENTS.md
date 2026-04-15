# Blog Update Workflow

## Overview

This is a Hexo blog hosted on GitHub Pages. The workflow separates **source files** (Markdown) from **generated files** (HTML).

## Update Process

1. **Edit source files** - Write posts in `source/_posts/` as Markdown files
2. **Push to remote** - Commit and push changes to GitHub
3. **GitHub Actions builds** - Automatically runs `hexo generate` to create HTML
4. **Deploy to Pages** - GitHub Pages serves the generated static files

## Key Directories

```
source/_posts/     # Markdown source files (posts)
themes/butterfly/  # Theme files
public/            # Generated HTML (auto-generated, not in git)
```

## Writing a New Post

Create a new Markdown file in `source/_posts/`:

```markdown
---
title: My New Post
date: 2026-04-15 12:00:00
categories:
  - Tech
tags:
  - Example
---

Your content here...
```

## Local Development

```bash
npm install           # Install dependencies
npx hexo server      # Preview locally (http://localhost:4000)
npx hexo generate    # Generate static files
```

## Build & Deploy

Push to `main` branch → GitHub Actions automatically:
1. Installs dependencies
2. Runs `hexo clean && hexo generate`
3. Deploys to GitHub Pages

## Notes

- Don't edit files in `public/` directly (they're auto-generated)
- Theme files in `themes/butterfly/` are committed to the repo
- Add images to `source/uploads/` or use external URLs
