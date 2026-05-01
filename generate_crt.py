import svgwrite
import requests
import random
import os

def create_crt_svg(username="Moty2111"):
    os.makedirs("assets", exist_ok=True)
    headers = {"Accept": "application/vnd.github.v3+json"}

    repos = 0
    followers = 0
    commits = 0
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        if r.status_code == 200:
            user = r.json()
            repos = user.get("public_repos", 0)
            followers = user.get("followers", 0)
    except:
        pass

    try:
        r_events = requests.get(f"https://api.github.com/users/{username}/events/public", headers=headers, timeout=10)
        if r_events.status_code == 200:
            events = r_events.json()
            commits = sum(1 for e in events if e.get("type") == "PushEvent")
    except:
        pass

    dwg = svgwrite.Drawing("assets/crt-stats.svg", size=(400, 200))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=8, fill="#0D1117"))

    # CRT scanlines
    for y in range(0, 200, 3):
        opacity = 0.15 if random.random() < 0.3 else 0.04
        dwg.add(dwg.rect(insert=(0, y), size=(400, 1), fill="#FFFFFF", opacity=opacity))

    if repos == 0 and followers == 0 and commits == 0:
        dwg.add(dwg.text("NO DATA", insert=(200, 100), fill="#FF4500",
                         font_size="24", text_anchor="middle", font_family="monospace"))
    else:
        dwg.add(dwg.text("📺 CRT MONITOR", insert=(200, 30), fill="#00FF41",
                         font_size="16", font_weight="bold", text_anchor="middle", font_family="monospace"))
        dwg.add(dwg.text(f"> Repos: {repos}", insert=(50, 70), fill="#00FF41",
                         font_size="12", font_family="monospace"))
        dwg.add(dwg.text(f"> Followers: {followers}", insert=(50, 95), fill="#00FF41",
                         font_size="12", font_family="monospace"))
        dwg.add(dwg.text(f"> Recent commits: {commits}", insert=(50, 120), fill="#00FF41",
                         font_size="12", font_family="monospace"))
        dwg.add(dwg.text("> STATUS: ONLINE", insert=(50, 145), fill="#00FF41",
                         font_size="12", font_family="monospace"))

    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(200, 185), fill="#006600",
                     font_size="8", text_anchor="middle", font_family="monospace"))

    try:
        dwg.save()
    except:
        with open("assets/crt-stats.svg", "w") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200"><rect width="400" height="200" fill="#0D1117" rx="8"/><text x="200" y="100" text-anchor="middle" fill="#FF4500" font-family="monospace" font-size="20">SVG ERROR</text></svg>')

if __name__ == "__main__":
    create_crt_svg()
