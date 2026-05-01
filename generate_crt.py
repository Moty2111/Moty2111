import svgwrite
import requests
import random
import os

def create_crt_svg(username="Moty2111"):
    os.makedirs("assets", exist_ok=True)
    headers = {"Accept": "application/vnd.github.v3+json"}

    # Данные
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        user = r.json()
        repos = user.get("public_repos", 0)
        followers = user.get("followers", 0)
    except:
        repos = 0
        followers = 0

    try:
        r_events = requests.get(f"https://api.github.com/users/{username}/events/public", headers=headers, timeout=10)
        events = r_events.json()
        commits = sum(1 for e in events if e.get("type") == "PushEvent")
    except:
        commits = 0

    # Эффект CRT: линии развёртки и помехи
    dwg = svgwrite.Drawing("assets/crt-stats.svg", size=(400, 200))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=8, fill="#0D1117"))

    # Развёртка
    for y in range(0, 200, 3):
        opacity = 0.1 if random.random() < 0.3 else 0.03
        dwg.add(dwg.rect(insert=(0, y), size=(400, 1), fill="#FFFFFF", opacity=opacity))

    # Текст
    dwg.add(dwg.text("📺 CRT MONITOR", insert=(200, 30), fill="#00FF41", font_size="16", font_weight="bold", text_anchor="middle", font_family="monospace"))
    dwg.add(dwg.text(f"> Repos: {repos}", insert=(50, 70), fill="#00FF41", font_size="12", font_family="monospace"))
    dwg.add(dwg.text(f"> Followers: {followers}", insert=(50, 95), fill="#00FF41", font_size="12", font_family="monospace"))
    dwg.add(dwg.text(f"> Recent commits: {commits}", insert=(50, 120), fill="#00FF41", font_size="12", font_family="monospace"))
    dwg.add(dwg.text("> STATUS: ONLINE", insert=(50, 145), fill="#00FF41", font_size="12", font_family="monospace"))

    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(200, 185), fill="#006600", font_size="8", text_anchor="middle", font_family="monospace"))
    dwg.save()

if __name__ == "__main__":
    create_crt_svg()
