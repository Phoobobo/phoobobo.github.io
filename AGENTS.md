# Agent Instructions

This is a Hexo-based blog deployed to GitHub Pages via GitHub Actions.

## Publishing a Post

### 1. Create a Markdown file in `source/_posts/`

File naming convention: `YYYY-MM-DD-slug.md`

Example: `source/_posts/2026-04-07-my-new-post.md`

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
git add source/_posts/YYYY-MM-DD-slug.md
git commit -m "post: Post Title"
git push origin master
```

Pushing to `master` automatically triggers GitHub Actions, which:
1. Runs `npm install && npm run build` at the repo root
2. Deploys the generated `public/` to GitHub Pages

The site is live at: https://phoobobo.github.io

## Repository Structure

```
source/_posts/        # Write all new posts here
_config.yml           # Hexo configuration
package.json          # Hexo dependencies
scaffolds/            # Post/page/draft templates
themes/               # Hexo themes
.github/workflows/    # GitHub Actions deploy workflow
```

## Rules

- Write posts in `source/_posts/` — this is the Hexo source directory
- Always use the `YYYY-MM-DD-slug.md` filename format
- front-matter fields `layout`, `title`, `date` are required
