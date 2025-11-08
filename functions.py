DANGER_LEVEL = {
    1: "🟢",
    2: "🟡",
    3: "🟡",
    4: "🟠",
    5: "🔴"
}

def get_scan_links(res : dict) -> dict[str, str]:
    d = {}
    for item in res["analysis"]["ingredients"]:
        if not item["referenceUrl"]:
            continue
        d[f"{DANGER_LEVEL[item['danger']]} {item['name'] if len(item["name"]) < 20 else (item['name'][:20] + '...')} {item['danger']} из 5"] = item["referenceUrl"]

    return d