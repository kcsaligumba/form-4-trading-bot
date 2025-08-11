import re
import httpx
from lxml import etree
from typing import List, Dict
from config import SEC_USER_AGENT

HEADERS = {"User-Agent": SEC_USER_AGENT}

ATOM_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&owner=only&output=atom"

def _dir_from_documents_href(href: str) -> str:
    # e.g. .../edgar/data/0000320193/0000320193-25-000012-index.html -> .../edgar/data/0000320193/0000320193-25-000012
    return href.rsplit("-", 1)[0].rstrip(".html")

def get_current_form4_entries(limit: int = 40) -> List[Dict]:
    r = httpx.get(ATOM_URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    root = etree.fromstring(r.content)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = []
    for e in root.xpath("//a:entry", namespaces=ns)[:limit]:
        link = e.xpath("string(a:link/@href)", namespaces=ns)
        title = e.xpath("string(a:title)", namespaces=ns)
        accession = re.search(r"(\d{10}-\d{2}-\d{6})", link)
        if not accession: 
            continue
        entries.append({
            "accession_no": accession.group(1),
            "documents_url": link,
            "dir_url": _dir_from_documents_href(link),
            "title": title
        })
    return entries
