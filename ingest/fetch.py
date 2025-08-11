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
    for f in data.get("directory", {}).get("item", []):
        name = f.get("name", "").lower()
        if name.endswith("ownership.xml"):
            return dir_url.rstrip("/") + "/" + f["name"]
    return None

def fetch_ownership_xml(xml_url: str) -> bytes:
    r = httpx.get(xml_url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.content
