from lxml import etree
from typing import Dict, Any, List

def parse_ownership_xml(xml_bytes: bytes) -> Dict[str, Any]:
    root = etree.fromstring(xml_bytes)
    ns = {"o": root.nsmap.get(None) or ""}

    def tx_val(node, path):
        s = node.xpath(f"string({path})", namespaces=ns)
        return s.strip() if s else ""

    issuer_symbol = root.xpath("string(//o:issuer/o:issuerTradingSymbol)", namespaces=ns).strip() or None
    filing_date = root.xpath("string(//o:periodOfReport)", namespaces=ns).strip() or None
    cik = root.xpath("string(//o:issuer/o:issuerCik)", namespaces=ns).strip() or None

    # Reporting owner info (take first)
    owner_name = root.xpath("string((//o:reportingOwner)[1]//o:rptOwnerName)", namespaces=ns).strip() or None
    is_officer = root.xpath("string((//o:reportingOwner)[1]//o:reportingOwnerRelationship/o:isOfficer)", namespaces=ns).strip() == "1"
    is_director = root.xpath("string((//o:reportingOwner)[1]//o:reportingOwnerRelationship/o:isDirector)", namespaces=ns).strip() == "1"
    officer_title = root.xpath("string((//o:reportingOwner)[1]//o:reportingOwnerRelationship/o:officerTitle)", namespaces=ns).strip() or None

    # Footnotes map
    footnotes = {}
    for fn in root.xpath("//o:footnote", namespaces=ns):
        fid = fn.attrib.get("id")
        if fid:
            footnotes[fid] = (fn.text or "").lower()

    transactions: List[Dict[str, Any]] = []
    for tx in root.xpath("//o:nonDerivativeTable//o:nonDerivativeTransaction", namespaces=ns):
        code = tx_val(tx, "o:transactionCoding/o:transactionCode")
        date = tx_val(tx, "o:transactionDate/o:value")
        shares = float(tx_val(tx, "o:transactionAmounts/o:transactionShares/o:value") or 0) or 0.0
        price = float(tx_val(tx, "o:transactionAmounts/o:transactionPricePerShare/o:value") or 0) or 0.0
        after = float(tx_val(tx, "o:postTransactionAmounts/o:sharesOwnedFollowingTransaction/o:value") or 0) or None

        # 10b5-1? (look in footnotes referenced by the transaction)
        is_plan = False
        for ref in tx.xpath(".//o:footnoteId", namespaces=ns):
            refid = ref.attrib.get("id")
            if refid and "10b5-1" in footnotes.get(refid, ""):
                is_plan = True
                break

        transactions.append({
            "transaction_code": code,
            "transaction_date": date,
            "shares": shares,
            "price": price,
            "shares_after": after,
            "is_10b5_1_plan": is_plan,
            "owner_name": owner_name,
            "is_officer": is_officer,
            "is_director": is_director,
            "officer_title": officer_title
        })

    return {
        "symbol": issuer_symbol,
        "filing_date": filing_date,
        "cik": cik,
        "transactions": transactions
    }
