# Agent Instructions

This is a Hexo-based blog deployed to GitHub Pages via GitHub Actions.

## Publishing a Post

### 1. Create a Markdown file in `_posts/`

File naming convention: `YYYY-MM-DD-slug.md`

Example: `_posts/2026-04-07-my-new-post.md`

### 2. Add front-matter and content

```yaml
---
layout: post
title: "Post Title"
date: 2026-04-07 10:00:00 +0800
categories: Category
tags: [tag1, tag2]
---

Post content in Markdown...
```

### 3. Commit and push to `master`

```bash
git add _posts/YYYY-MM-DD-slug.md
git commit -m "post: Post Title"
git push origin master
```

Pushing to `master` automatically triggers GitHub Actions, which:
1. Copies `_posts/*.md` into `hexo-site/source/_posts/`
2. Runs `npm install && npm run build` inside `hexo-site/`
3. Deploys the generated `hexo-site/public/` to GitHub Pages

The site is live at: https://phoobobo.github.io

## Repository Structure

```
_posts/               # Write all new posts here
hexo-site/            # Hexo source (config, themes, scaffolds)
  _config.yml         # Hexo configuration
  source/_posts/      # Auto-populated by CI — do not edit manually
.github/workflows/    # GitHub Actions deploy workflow
```

## Rules

- Only write posts in `_posts/` at the repo root — never directly in `hexo-site/source/_posts/`
- Always use the `YYYY-MM-DD-slug.md` filename format
- front-matter fields `layout`, `title`, `date` are required
