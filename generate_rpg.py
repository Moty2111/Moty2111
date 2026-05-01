import svgwrite
import requests
import os
import traceback

def create_rpg_svg(username="Moty2111"):
    os.makedirs("assets", exist_ok=True)
    headers = {"Accept": "application/vnd.github.v3+json"}

    # Пытаемся получить данные
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

    # Генерация SVG
    dwg = svgwrite.Drawing("assets/rpg-stats.svg", size=(400, 200))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=8, fill="#0D1117"))
    dwg.add(dwg.text("🎮 RPG CHARACTER", insert=(200, 30), fill="#FFD700",
                     font_size="16", font_weight="bold", text_anchor="middle", font_family="monospace"))

    if repos == 0 and followers == 0 and commits == 0:
        dwg.add(dwg.text("NO DATA", insert=(200, 100), fill="#FF4500",
                         font_size="24", text_anchor="middle", font_family="monospace"))
    else:
        stats = [
            ("⚔️ Strength", min(commits * 2, 100)),
            ("🛡️ Defense", min(repos * 5, 100)),
            ("💡 Intelligence", min(followers * 10, 100)),
            ("❤️ Health", 100)
        ]
        y = 60
        for label, value in stats:
            dwg.add(dwg.text(label, insert=(100, y), fill="#8E9AAF",
                             font_size="12", font_family="monospace"))
            # Progress bar
            dwg.add(dwg.rect(insert=(200, y-10), size=(160, 10), rx=4, fill="#30363D"))
            bar_w = int(160 * value / 100)
            if bar_w > 0:
                dwg.add(dwg.rect(insert=(200, y-10), size=(bar_w, 10), rx=4, fill="#58A6FF"))
            dwg.add(dwg.text(str(value), insert=(370, y), fill="#58A6FF",
                             font_size="10", text_anchor="middle", font_family="monospace"))
            y += 25

    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(200, 185), fill="#6C7A89",
                     font_size="8", text_anchor="middle", font_family="monospace"))
    try:
        dwg.save()
    except Exception as e:
        # fallback: записываем минимальный SVG вручную
        with open("assets/rpg-stats.svg", "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200"><rect width="400" height="200" fill="#0D1117" rx="8"/><text x="200" y="100" text-anchor="middle" fill="#FF4500" font-family="monospace" font-size="20">SVG ERROR</text></svg>')

if __name__ == "__main__":
    create_rpg_svg()
