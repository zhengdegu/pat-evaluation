import csv
import time
import random
import sys
import urllib.parse
from typing import Dict, Iterable, List, Optional, Tuple
import os

import requests
from bs4 import BeautifulSoup, Tag


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.patent9.com/",
}


SEARCH_BASES = [
    # Known common patterns; the site may support one of these.
    "https://www.patent9.com/search.html?q={query}&p={page}",
    "https://www.patent9.com/search?q={query}&p={page}",
    "https://www.patent9.com/search.html?kw={query}&p={page}",
    # Additional commonly seen patterns
    "https://www.patent9.com/s?wd={query}&p={page}",
    "https://www.patent9.com/search?wd={query}&p={page}",
    "https://www.patent9.com/search.html?wd={query}&p={page}",
]

DETAIL_LINK_HINTS = ("/patent/", "/view/", "/cn/", "/zhuanli/")

# Desired output columns
COLUMN_NAMES = [
    "专利名",
    "申请号",
    "申请日",
    "摘要",
    "申请人",
    "申请人地址",
    "发明人",
    "IPC分类号",
    "公开号",
    "公开日",
    "主分类号",
    "转化收益（万元）",
]

def sleep_jitter(min_seconds: float = 0.8, max_seconds: float = 1.8) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))


def request_html(url: str, session: Optional[requests.Session] = None) -> Optional[str]:
    sess = session or requests.Session()
    try:
        resp = sess.get(url, headers=DEFAULT_HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        # Some servers may not set a classic text/html header; accept body if non-empty
        text = resp.text or ""
        return text if text.strip() else None
    except requests.RequestException:
        return None


def build_search_urls(keyword: str, max_pages: int) -> List[str]:
    encoded = urllib.parse.quote(keyword)
    urls: List[str] = []
    for page in range(1, max_pages + 1):
        for base in SEARCH_BASES:
            urls.append(base.format(query=encoded, page=page))
    return urls


def extract_list_links(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    links: List[str] = []
    # Try common result containers to bias towards top results
    containers = []
    containers.extend(soup.select(".result, .results, .list, .items, .search-result"))
    if not containers:
        containers = [soup]
    for container in containers:
        for a in container.find_all("a", href=True):
            href = a["href"].strip()
            if any(hint in href for hint in DETAIL_LINK_HINTS):
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = "https://www.patent9.com" + href
                if href not in links:
                    links.append(href)
    if links:
        return links
    # Fallback: global scan
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if any(hint in href for hint in DETAIL_LINK_HINTS):
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                href = "https://www.patent9.com" + href
            # De-duplicate while preserving order
            if href not in links:
                links.append(href)
    return links


def _extract_by_label(soup: BeautifulSoup, label_texts: Iterable[str]) -> Optional[str]:
    # Try common table/dl patterns where a label cell is followed by a value cell
    label_candidates = list(label_texts)
    for label in label_candidates:
        # direct text match in elements
        el = soup.find(lambda tag: isinstance(tag, Tag) and tag.get_text(strip=True) == label)
        if el:
            # Try next sibling text
            next_el = el.find_next_sibling()
            if next_el and isinstance(next_el, Tag):
                text = next_el.get_text(" ", strip=True)
                if text:
                    return text
            # Try parent-row pattern (e.g., <tr><th>label</th><td>value</td></tr>)
            parent = el.parent
            if parent and isinstance(parent, Tag):
                tds = parent.find_all(["td", "dd"])
                if len(tds) >= 1:
                    text = tds[-1].get_text(" ", strip=True)
                    if text:
                        return text
    # Fallback: fuzzy search
    for label in label_candidates:
        el = soup.find(string=lambda s: isinstance(s, str) and label in s)
        if el:
            container = el.parent if hasattr(el, "parent") else None
            if container and isinstance(container, Tag):
                sib = container.find_next_sibling()
                if sib and isinstance(sib, Tag):
                    text = sib.get_text(" ", strip=True)
                    if text:
                        return text
    return None


def parse_detail_page(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "lxml")

    def text_or_none(x: Optional[str]) -> Optional[str]:
        return x.strip() if isinstance(x, str) and x.strip() else None

    # Title
    title = None
    if soup.title:
        title = soup.title.get_text(strip=True)
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True) or title

    # Fields by label
    application_number = _extract_by_label(soup, ["申请号", "申请（专利）号"])
    application_date = _extract_by_label(soup, ["申请日", "申请日期"])
    abstract_text = None
    abstract_node = soup.find("div", class_=lambda c: c and ("abstr" in c or "abstract" in c))
    if abstract_node:
        abstract_text = abstract_node.get_text(" ", strip=True)
    if not abstract_text:
        abstract_text = _extract_by_label(soup, ["摘要"])

    applicant = _extract_by_label(soup, ["申请人", "专利权人"])
    applicant_address = _extract_by_label(soup, ["申请人地址", "地址"])
    inventors = _extract_by_label(soup, ["发明人"])
    ipc = _extract_by_label(soup, ["IPC分类号", "国际分类号", "分类号"])
    publication_number = _extract_by_label(soup, ["公开号", "公布/公告号"])
    publication_date = _extract_by_label(soup, ["公开日", "公布/公告日"])
    main_classification = _extract_by_label(soup, ["主分类号"])

    # This field likely isn't on the site; leave blank for now
    conversion_income = None

    return {
        "专利名": text_or_none(title),
        "申请号": text_or_none(application_number),
        "申请日": text_or_none(application_date),
        "摘要": text_or_none(abstract_text),
        "申请人": text_or_none(applicant),
        "申请人地址": text_or_none(applicant_address),
        "发明人": text_or_none(inventors),
        "IPC分类号": text_or_none(ipc),
        "公开号": text_or_none(publication_number),
        "公开日": text_or_none(publication_date),
        "主分类号": text_or_none(main_classification),
        "转化收益（万元）": text_or_none(conversion_income),
    }


def scrape_patents(keyword: str, max_pages: int = 3, max_per_page: int = 20) -> List[Dict[str, Optional[str]]]:
    session = requests.Session()
    # Inject cookie if provided (may be needed to bypass anti-bot)
    cookie = os.environ.get("PATENT9_COOKIE")
    if cookie:
        DEFAULT_HEADERS["Cookie"] = cookie
    results: List[Dict[str, Optional[str]]] = []
    seen_detail_links: set[str] = set()

    # Try each pattern per page; continue across patterns
    used_patterns: set[str] = set()

    for page in range(1, max_pages + 1):
        page_links_collected = 0
        for base in SEARCH_BASES:
            search_url = base.format(query=urllib.parse.quote(keyword), page=page)
            html = request_html(search_url, session=session)
            sleep_jitter()
            if not html:
                print(f"[WARN] Empty HTML for {search_url}")
                continue
            links = extract_list_links(html)
            if not links:
                print(f"[INFO] No detail links detected on {search_url}")
                continue
            used_patterns.add(base)
            for link in links:
                if link in seen_detail_links:
                    continue
                seen_detail_links.add(link)
                detail_html = request_html(link, session=session)
                sleep_jitter()
                if not detail_html:
                    print(f"[WARN] Failed to load detail page: {link}")
                    continue
                row = parse_detail_page(detail_html)
                results.append(row)
                page_links_collected += 1
                if page_links_collected >= max_per_page:
                    break
            if page_links_collected >= max_per_page:
                break
        # If after trying all bases we still have nothing on this page, assume no more results
        if page_links_collected == 0:
            print(f"[INFO] Page {page}: collected 0 items; stopping.")
            break
    return results


def write_csv(rows: List[Dict[str, Optional[str]]], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMN_NAMES)
        writer.writeheader()
        for row in rows:
            # Ensure all keys exist
            safe_row = {key: (row.get(key) or "") for key in COLUMN_NAMES}
            writer.writerow(safe_row)


def main(argv: List[str]) -> int:
    # Usage: python scripts/patent9_scrape.py 药品 output.csv 3 20
    if len(argv) < 3:
        print("Usage: python scripts/patent9_scrape.py <keyword> <output_csv> [max_pages] [max_per_page]", file=sys.stderr)
        return 2
    keyword = argv[1]
    output_csv = argv[2]
    max_pages = int(argv[3]) if len(argv) >= 4 else 3
    max_per_page = int(argv[4]) if len(argv) >= 5 else 20
    if len(argv) >= 6:
        os.environ["PATENT9_COOKIE"] = argv[5]

    print(f"Searching Patent9 for keyword: {keyword} (pages={max_pages}, per_page={max_per_page})")
    rows = scrape_patents(keyword=keyword, max_pages=max_pages, max_per_page=max_per_page)
    print(f"Found {len(rows)} records. Writing to {output_csv} ...")
    write_csv(rows, output_csv)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


