#!/usr/bin/env python3
# Simple static post generator for Hexo/NexT-like static site
# Scans _posts/*.md and generates HTML pages under YYYY/MM/DD/slug/index.html

import os, re, sys
from datetime import datetime

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
POSTS_DIR = os.path.join(ROOT, '_posts')
TEMPLATE_SEARCH_DIR = os.path.join(ROOT)
INDEX_HTML = os.path.join(ROOT, 'index.html')

if not os.path.isdir(POSTS_DIR):
    print('No _posts folder found:', POSTS_DIR)
    sys.exit(1)

# find a template post HTML to reuse
template_path = None
for root, dirs, files in os.walk(ROOT):
    for fn in files:
        if fn == 'index.html' and ('2017' in root or '2018' in root or re.search(r'/20\d{2}/', root)):
            path = os.path.join(root, fn)
            with open(path, encoding='utf-8') as f:
                txt = f.read()
            if '<div class="post-body"' in txt:
                template_path = path
                template_html = txt
                break
    if template_path:
        break

if not template_path:
    print('Template post not found. Aborting.')
    sys.exit(1)

print('Using template:', template_path)

# helper to slugify filename\ndef slug_from_filename(fname):
    base = os.path.basename(fname)
    if base.count('-') >= 3:
        parts = base.split('-')
        date = '-'.join(parts[:3])
        slug = '-'.join(parts[3:]).rsplit('.',1)[0]
        return date, slug
    else:
        m = re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\\.md$', base)
        if m:
            return m.group(1), m.group(2)
        else:
            dt = datetime.fromtimestamp(os.path.getmtime(fname))
            return dt.strftime('%Y-%m-%d'), os.path.splitext(base)[0]

# parse front matter (naive)
def split_frontmatter(md_text):
    if md_text.startswith('---'):
        parts = md_text.split('---')
        if len(parts) >= 3:
            fm = parts[1]
            body = '---'.join(parts[2:]).strip()
            title = None
            date = None
            for line in fm.splitlines():
                if line.strip().startswith('title:'):
                    title = line.split(':',1)[1].strip().strip('"').strip("'")
                if line.strip().startswith('date:'):
                    date = line.split(':',1)[1].strip()
            return fm, title, date, body
    return None, None, None, md_text

try:
    import markdown
    HAS_MD = True
except Exception:
    HAS_MD = False

for fn in sorted(os.listdir(POSTS_DIR)):
    if not fn.lower().endswith('.md'):
        continue
    path = os.path.join(POSTS_DIR, fn)
    with open(path, encoding='utf-8') as f:
        md = f.read()
    fm, title, date_meta, body = split_frontmatter(md)
    date_from_file, slug = slug_from_filename(fn)
    post_date = date_meta or date_from_file
    if HAS_MD:
        html_body = markdown.markdown(body, extensions=['fenced_code','codehilite','tables'])
    else:
        html_body = ''
        for block in re.split(r'\n\n+', body):
            block = block.strip()
            if block.startswith('# '):
                html_body += '<h1>' + block[2:].strip() + '</h1>\n'
            elif block.startswith('## '):
                html_body += '<h2>' + block[3:].strip() + '</h2>\n'
            else:
                html_body += '<p>' + block.replace('\n','<br>') + '</p>\n'
    y,m,d = post_date.split(' ')[0].split('-') if ' ' in post_date else post_date.split('-')
    outdir = os.path.join(ROOT, y, m, d, slug)
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, 'index.html')
    new_html = template_html
    new_html = re.sub(r'(<h1[^>]*class="post-title"[^>]*>).*?(</h1>)', r"\1" + (title or slug) + r"\2", new_html, flags=re.S)
    new_html = re.sub(r'(<h1[^>]*itemprop="name headline"[^>]*>).*?(</h1>)', r"\1" + (title or slug) + r"\2", new_html, flags=re.S)
    new_html = re.sub(r'itemprop="dateCreated datePublished" datetime="[^"]+"', 'itemprop="dateCreated datePublished" datetime="%s"' % (post_date.replace(' ', 'T') + '+08:00'), new_html)
    new_html = re.sub(r'<meta property="og:updated_time" content="[^"]+"', '<meta property="og:updated_time" content="%s"' % (post_date.replace(' ', 'T') + '+08:00'), new_html)
    new_html = re.sub(r'(<div class="post-body"[^>]*>).*?(</div>)', r"\1\n" + html_body + r"\n\2", new_html, flags=re.S)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print('Wrote', outpath)

if os.path.exists(INDEX_HTML):
    with open(INDEX_HTML, encoding='utf-8') as f:
        base = f.read()
    m = re.search(r'(<article[\s\S]*?</article>)', new_html)
    snippet = m.group(1) if m else ''
    if snippet and 'openclaw-multi-agent-rebuild' in outpath:
        if snippet not in base:
            pos = base.find('<section id="posts"')
            if pos != -1:
                pos2 = base.find('>', pos)
                new_base = base[:pos2+1] + '\n' + snippet + '\n' + base[pos2+1:]
                with open(INDEX_HTML, 'w', encoding='utf-8') as f:
                    f.write(new_base)
                print('Inserted snippet into index.html')

print('Done')
