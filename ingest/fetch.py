import httpx, json
from config import SEC_USER_AGENT
from typing import Optional

HEADERS = {"User-Agent": SEC_USER_AGENT}

def find_ownership_xml_url(dir_url: str) -> Optional[str]:
    # Most EDGAR directories expose a JSON listing
    idx = dir_url.rstrip("/") + "/index.json"
    r = httpx.get(idx, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        return None
    data = r.json()
    items = data.get("directory", {}).get("item", [])
    preferred = []
    fallback = []
    for f in items:
        name = f.get("name", "")
        lname = name.lower()
        if not lname.endswith(".xml"):
            continue
        if lname.endswith(("xsl.xml", "xsd.xml")):
            continue
        if lname in ("filingsummary.xml",):
            continue
        if any(k in lname for k in ("ownership", "form4", "primary")):
            preferred.append(name)
        else:
            fallback.append(name)
    if preferred:
        return dir_url.rstrip("/") + "/" + preferred[0]
    if fallback:
        return dir_url.rstrip("/") + "/" + fallback[0]
    return None

def fetch_ownership_xml(xml_url: str) -> bytes:
    r = httpx.get(xml_url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.content
