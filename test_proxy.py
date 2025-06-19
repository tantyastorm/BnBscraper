import requests

proxy = "http://123.456.789.000:8080"  # example from free-proxy-list.net
try:
    r = requests.get("https://www.airbnb.com", proxies={"http": proxy, "https": proxy}, timeout=5)
    print(r.status_code, r.text[:200])
except Exception as e:
    print("Proxy failed:", e)