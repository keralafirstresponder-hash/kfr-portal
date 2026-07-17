import requests

BASE = "http://localhost:3000"

URLS = [
    "https://images.unsplash.com/photo-1755549746560-f56c7bd0c82f?auto=format&fit=crop&w=2000&q=85",
    "https://images.unsplash.com/photo-1579037005241-a79202c7e9fd?auto=format&fit=crop&w=2000&q=85",
    "https://images.unsplash.com/photo-1769791687730-52b608addf88?auto=format&fit=crop&w=1400&q=85",
    "https://images.unsplash.com/photo-1592050103688-a6053fc0e386?auto=format&fit=crop&w=2000&q=85",
    f"{BASE}/assets/kfr-shield.png",
    f"{BASE}/assets/aster-medcity-logo.png",
    f"{BASE}/assets/wisdom4future-logo.png",
    f"{BASE}/assets/befirst-logo.png",
]

failures = []
for url in URLS:
    try:
        resp = requests.get(url, timeout=20, stream=True, headers={"User-Agent": "Mozilla/5.0 QA Asset Check"})
        content_type = resp.headers.get("content-type", "")
        size = int(resp.headers.get("content-length") or 0)
        print(f"{resp.status_code} {content_type} {size} {url}")
        if resp.status_code != 200 or "image" not in content_type.lower():
            failures.append(f"Bad asset response: {resp.status_code} {content_type} {url}")
    except Exception as exc:
        failures.append(f"Exception for {url}: {exc}")

if failures:
    raise SystemExit("\n".join(failures))