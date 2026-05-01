import svgwrite
import requests
import os

def create_rpg_svg(username="Moty2111"):
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

    # Генерация SVG
    dwg = svgwrite.Drawing("assets/rpg-stats.svg", size=(400, 200))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=8, fill="#0D1117"))
    dwg.add(dwg.text("🎮 RPG CHARACTER", insert=(200, 30), fill="#FFD700", font_size="16", font_weight="bold", text_anchor="middle", font_family="monospace"))

    # Статы
    stats = [
        ("⚔️ Strength", min(commits * 2, 100)),
        ("🛡️ Defense", min(repos * 5, 100)),
        ("💡 Intelligence", min(followers * 10, 100)),
        ("❤️ Health", 100)
    ]
    y = 60
    for label, value in stats:
        dwg.add(dwg.text(label, insert=(100, y), fill="#8E9AAF", font_size="12", font_family="monospace"))
        # Progress bar
        dwg.add(dwg.rect(insert=(200, y-10), size=(160, 10), rx=4, fill="#30363D"))
        dwg.add(dwg.rect(insert=(200, y-10), size=(int(160*value/100), 10), rx=4, fill="#58A6FF"))
        dwg.add(dwg.text(str(value), insert=(370, y), fill="#58A6FF", font_size="10", text_anchor="middle", font_family="monospace"))
        y += 25

    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(200, 185), fill="#6C7A89", font_size="8", text_anchor="middle", font_family="monospace"))
    dwg.save()

if __name__ == "__main__":
    create_rpg_svg()
