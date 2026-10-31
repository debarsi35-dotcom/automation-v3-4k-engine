"""pipeline/market_ideator.py — Market-Driven Viral Ideation & Live YouTube RSS Scraper."""
import urllib.request, xml.etree.ElementTree as ET

BENCHMARK_CHANNELS = {
    "TED-Ed": "UCsooa4yRKGN_zEE8iknghZA",
    "Kurzgesagt": "UCsXVk37bltHxD1rDPwtNM8Q",
    "Veritasium": "UCHnyfMqiRRG1u-2MsSQLbXA",
    "Vsauce": "UC6nSFpj9HTCZ5t-N3Rm3-HA",
}

def fetch_live_youtube_signals() -> list[str]:
    signals = []
    for name, cid in BENCHMARK_CHANNELS.items():
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                root = ET.fromstring(r.read())
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall("atom:entry", ns)[:4]:
                    t = entry.find("atom:title", ns)
                    if t is not None and t.text:
                        signals.append(f"[{name}] {t.text}")
        except Exception:
            pass
    if not signals:
        signals = [
            "[Ifverse] What If You Had 500 IQ? (1.4M views)",
            "[Ifverse] What If One Second Felt Like Ten? (678K views)",
            "[Day One Films] What If Your Reaction Time Was 10x Faster? (5.1M views)",
            "[TED-Ed] What if you didn't brush your teeth for a year? (495K views)",
            "[TED-Ed] 4 ways to fix your attention span (4.4M views)",
        ]
    return signals
