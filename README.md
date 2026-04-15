# phoobobo's Blog

A Hexo blog powered by Butterfly theme, deployed on GitHub Pages.

## Branch Usage

| Branch | Content | Purpose |
|--------|---------|---------|
| `master` | Source code (Markdown + Hexo config) | Edit posts, auto-deploys on push |
| `gh-pages` | Compiled HTML | Auto-generated, don't edit manually |

## Daily Workflow

1. Edit `source/_posts/*.md` on `master` branch
2. Push → GitHub Actions builds automatically
3. Deploys to `gh-pages`

## Local Development

```bash
npm install           # Install dependencies
npx hexo server       # Preview at http://localhost:4000
npx hexo generate     # Generate static files
```

## Commands

```bash
git checkout master           # Switch to source branch
git add . && git commit -m "..." && git push  # Push changes
```

## Notes

- Don't edit files in `public/` directly (auto-generated)
- Theme files are in `themes/butterfly/`
- Add images to `source/uploads/` or use external URLs
