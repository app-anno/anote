#!/usr/bin/env python3
"""Parse YYYYMMDD-trend.md and generate X-style feed HTML."""
import re, sys, html
import urllib.request
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_trend(md_text):
    articles = []
    seen_urls = set()

    sections = re.split(r'^## ', md_text, flags=re.MULTILINE)

    for section in sections:
        if not section.strip():
            continue

        section_header = section.split('\n')[0].strip()

        if section_header.startswith('Claude Code'):
            parse_claude_code(section, articles, seen_urls)
        elif 'はてブ' in section_header:
            parse_hatena(section, articles, seen_urls)
        elif 'Hacker News' in section_header:
            parse_hn(section, articles, seen_urls)
        elif 'Reddit テック系' in section_header:
            parse_reddit(section, articles, seen_urls, 'reddit-tech', 'Reddit')
        elif 'パレオな男' in section_header:
            parse_paleo(section, articles, seen_urls)
        elif 'PubMed' in section_header:
            parse_pubmed(section, articles, seen_urls)
        elif 'Reddit フィットネス系' in section_header:
            parse_reddit(section, articles, seen_urls, 'reddit-fitness', 'Reddit Fitness')

    return articles

def extract_link(text):
    m = re.search(r'\[([^\]]*)\]\(([^)]+)\)', text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return text.strip(), ''

def stars_count(text):
    if '★★★' in text:
        return 3
    elif '★★' in text:
        return 2
    elif '★' in text:
        return 1
    return 0

def add_article(articles, seen_urls, art, priority=False):
    url = art.get('url', '')
    if url and url in seen_urls:
        if not priority:
            return
    if url:
        seen_urls.add(url)
    articles.append(art)

def parse_table_rows(text):
    rows = []
    for line in text.split('\n'):
        line = line.strip()
        if not line.startswith('|') or line.startswith('|--') or line.startswith('|-'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if any('---' in c for c in cells):
            continue
        rows.append(cells)
    return rows[1:] if rows else []  # skip header

def parse_claude_code(section, articles, seen_urls):
    rows = parse_table_rows(section)
    for row in rows:
        if len(row) < 3:
            continue
        title = row[0].strip()
        summary = row[1].strip()
        source_cell = row[2].strip()
        _, url = extract_link(source_cell)
        if not title or title == '項目':
            continue
        add_article(articles, seen_urls, {
            'title': title, 'url': url,
            'source': 'claude-code', 'sourceLabel': 'Claude Code',
            'stars': 2, 'metric': '', 'metricValue': 0,
            'category': 'AI開発', 'summary': summary
        }, priority=True)

def parse_hatena(section, articles, seen_urls):
    subsections = re.split(r'^### ', section, flags=re.MULTILINE)
    for sub in subsections:
        sub_header = sub.split('\n')[0].strip()
        if '注目トピック' in sub_header:
            rows = parse_table_rows(sub)
            for row in rows:
                if len(row) < 5:
                    continue
                title, url = extract_link(row[0])
                if not title or title == 'タイトル':
                    continue
                bm = re.search(r'(\d+)', row[1])
                mv = int(bm.group(1)) if bm else 0
                add_article(articles, seen_urls, {
                    'title': title, 'url': url,
                    'source': 'hatena', 'sourceLabel': 'はてブ',
                    'stars': stars_count(row[2]), 'metric': 'users',
                    'metricValue': mv, 'category': row[3].strip(),
                    'summary': row[4].strip()
                }, priority=True)
        elif '全エントリー' in sub_header:
            parse_numbered_list(sub, articles, seen_urls, 'hatena', 'はてブ', 'users')

def parse_hn(section, articles, seen_urls):
    subsections = re.split(r'^### ', section, flags=re.MULTILINE)
    for sub in subsections:
        sub_header = sub.split('\n')[0].strip()
        if '注目トピック' in sub_header:
            rows = parse_table_rows(sub)
            for row in rows:
                if len(row) < 5:
                    continue
                title, url = extract_link(row[0])
                if not title or title == 'タイトル':
                    continue
                pt = re.search(r'(\d+)', row[1])
                mv = int(pt.group(1)) if pt else 0
                add_article(articles, seen_urls, {
                    'title': title, 'url': url,
                    'source': 'hn', 'sourceLabel': 'HN',
                    'stars': stars_count(row[2]), 'metric': 'pt',
                    'metricValue': mv, 'category': row[3].strip(),
                    'summary': row[4].strip()
                }, priority=True)
        elif '全エントリー' in sub_header:
            parse_numbered_list(sub, articles, seen_urls, 'hn', 'HN', 'pt')

def parse_reddit(section, articles, seen_urls, source, source_label):
    subsections = re.split(r'^### ', section, flags=re.MULTILINE)
    for sub in subsections:
        sub_header = sub.split('\n')[0].strip()
        if '注目トピック' in sub_header:
            rows = parse_table_rows(sub)
            for row in rows:
                if len(row) < 7:
                    continue
                title, url = extract_link(row[0])
                if not title or title == 'タイトル':
                    continue
                ups = re.search(r'(\d+)', row[1])
                mv = int(ups.group(1)) if ups else 0
                add_article(articles, seen_urls, {
                    'title': title, 'url': url,
                    'source': source, 'sourceLabel': source_label,
                    'stars': stars_count(row[3]), 'metric': 'ups',
                    'metricValue': mv, 'category': row[4].strip(),
                    'summary': row[6].strip()
                }, priority=True)
        elif 'カテゴリ別エントリー' in sub_header:
            parse_numbered_list(sub, articles, seen_urls, source, source_label, 'ups')

def parse_numbered_list(text, articles, seen_urls, source, source_label, metric):
    for line in text.split('\n'):
        line = line.strip()
        m = re.match(r'^\d+\.\s+\[([^\]]+)\]\(([^)]+)\)\s*\((\d[\d,]*)\s*(users|pt|ups)', line)
        if not m:
            continue
        title = m.group(1)
        url = m.group(2)
        mv = int(m.group(3).replace(',', ''))
        summary_m = re.search(r'-\s*(?:r/\S+\s*-\s*)?(.+)$', line)
        summary = summary_m.group(1).strip() if summary_m else ''
        add_article(articles, seen_urls, {
            'title': title, 'url': url,
            'source': source, 'sourceLabel': source_label,
            'stars': 0, 'metric': metric, 'metricValue': mv,
            'category': '', 'summary': summary
        })

def parse_paleo(section, articles, seen_urls):
    rows = parse_table_rows(section)
    for row in rows:
        if len(row) < 5:
            continue
        title, url = extract_link(row[0])
        if not title or title == 'タイトル':
            continue
        add_article(articles, seen_urls, {
            'title': title, 'url': url,
            'source': 'paleo', 'sourceLabel': 'パレオな男',
            'stars': stars_count(row[3]), 'metric': '', 'metricValue': 0,
            'category': row[2].strip(), 'summary': row[4].strip()
        }, priority=True)

def parse_pubmed(section, articles, seen_urls):
    subsections = re.split(r'^### ', section, flags=re.MULTILINE)
    for sub in subsections:
        sub_header = sub.split('\n')[0].strip()
        if any(k in sub_header for k in ['運動', '栄養', '睡眠']):
            cat = sub_header
            rows = parse_table_rows(sub)
            for row in rows:
                if len(row) < 5:
                    continue
                title, url = extract_link(row[0])
                if not title or '論文タイトル' in title:
                    continue
                journal = row[1].strip()
                summary_text = row[4].strip()
                if journal:
                    summary_text = f"[{journal}] {summary_text}"
                add_article(articles, seen_urls, {
                    'title': title, 'url': url,
                    'source': 'pubmed', 'sourceLabel': 'PubMed',
                    'stars': stars_count(row[3]), 'metric': '', 'metricValue': 0,
                    'category': cat, 'summary': summary_text
                }, priority=True)

def fetch_article_content(url, timeout=10):
    """Fetch article and extract text content."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'ja,en;q=0.9',
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
            ct = resp.headers.get('Content-Type', '')
            enc = 'utf-8'
            if 'charset=' in ct:
                enc = ct.split('charset=')[-1].strip().split(';')[0]
            try:
                page = raw.decode(enc)
            except Exception:
                page = raw.decode('utf-8', errors='ignore')

        # Try meta description first
        meta_desc = ''
        m = re.search(r'<meta\s+(?:name|property)=["\'](?:description|og:description)["\']\s+content=["\']([^"\']+)', page, re.IGNORECASE)
        if not m:
            m = re.search(r'content=["\']([^"\']+)["\']\s+(?:name|property)=["\'](?:description|og:description)', page, re.IGNORECASE)
        if m:
            meta_desc = html.unescape(m.group(1)).strip()

        # Try to extract article/main body
        text = page
        # Remove script/style/nav/header/footer
        for tag in ['script', 'style', 'nav', 'header', 'footer', 'aside']:
            text = re.sub(rf'<{tag}[^>]*>[\s\S]*?</{tag}>', '', text, flags=re.IGNORECASE)

        # Prefer <article> or <main> content
        article_m = re.search(r'<article[^>]*>([\s\S]*?)</article>', text, re.IGNORECASE)
        if article_m:
            text = article_m.group(1)
        else:
            main_m = re.search(r'<main[^>]*>([\s\S]*?)</main>', text, re.IGNORECASE)
            if main_m:
                text = main_m.group(1)

        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Use body text if substantial, otherwise meta description
        if len(text) >= 200:
            return text[:800].strip()
        elif meta_desc and len(meta_desc) >= 50:
            return meta_desc[:800].strip()
        elif meta_desc:
            return meta_desc
        return None
    except Exception:
        return None

def enrich_articles(articles):
    """Fetch content for ★★★ articles to replace short MD summaries."""
    starred = [(i, a) for i, a in enumerate(articles) if a['stars'] >= 3 and a['url']]
    if not starred:
        return

    print(f"Fetching content for {len(starred)} starred articles...")
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}
        for i, a in starred:
            futures[executor.submit(fetch_article_content, a['url'])] = (i, a['title'])
        for future in as_completed(futures):
            idx, title = futures[future]
            content = future.result()
            if content and len(content) > len(articles[idx]['summary']):
                results[idx] = content

    for idx, content in results.items():
        articles[idx]['summary'] = content

    print(f"  Enriched {len(results)}/{len(starred)} articles with fetched content")

def sort_articles(articles):
    def sort_key(a):
        return (-a['stars'], -a['metricValue'])
    articles.sort(key=sort_key)

def make_stars_str(n):
    return '★' * n if n > 0 else ''

def make_card(a):
    s = a['source']
    sl = html.escape(a['sourceLabel'])
    stars = a['stars']
    title = html.escape(a['title'])
    url = a['url']
    summary = html.escape(a['summary']) if a['summary'] else ''
    category = html.escape(a['category']) if a['category'] else ''
    mv = a['metricValue']
    metric = a['metric']

    lines = [f'    <article class="card" data-stars="{stars}" data-source="{s}">']
    lines.append(f'      <div class="card-header">')
    lines.append(f'        <span class="source-badge {s}">{sl}</span>')
    if stars > 0:
        lines.append(f'        <span class="stars">{make_stars_str(stars)}</span>')
    if mv > 0 and metric:
        lines.append(f'        <span class="metric">{mv:,} {metric}</span>')
    lines.append(f'      </div>')
    if url:
        lines.append(f'      <h2 class="card-title"><a href="{html.escape(url)}" target="_blank" rel="noopener">{title}</a></h2>')
    else:
        lines.append(f'      <h2 class="card-title">{title}</h2>')
    if summary:
        lines.append(f'      <div class="card-body">')
        lines.append(f'        <p class="card-text">{summary}</p>')
        lines.append(f'      </div>')
    if category:
        lines.append(f'      <div class="card-footer">')
        lines.append(f'        <span class="category-tag">{category}</span>')
        lines.append(f'      </div>')
    lines.append(f'    </article>')
    return '\n'.join(lines)

def main():
    md_path = sys.argv[1]
    template_path = sys.argv[2]
    output_path = sys.argv[3]
    date_str = sys.argv[4]

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    articles = parse_trend(md_text)
    enrich_articles(articles)
    sort_articles(articles)

    cards_html = '\n'.join(make_card(a) for a in articles)
    total = len(articles)

    result = template.replace('{{FEED_ITEMS}}', cards_html)
    result = result.replace('{{GENERATED_DATE}}', date_str)
    result = result.replace('{{TOTAL_COUNT}}', str(total))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Generated {output_path} with {total} articles")

if __name__ == '__main__':
    main()
