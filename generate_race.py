import svgwrite
import requests
import os
from datetime import datetime

def create_race_svg(username="Moty2111"):
    # Создаём папку assets, если её нет
    os.makedirs("assets", exist_ok=True)

    # Получаем публичные события
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(f"https://api.github.com/users/{username}/events/public", 
                        headers=headers, timeout=10)
        events = r.json()
        commits_today = sum(1 for e in events if e.get("type") == "PushEvent")
    except:
        commits_today = 0

    # Информация о пользователе
    try:
        r2 = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        user = r2.json()
        repos = user.get("public_repos", 0)
        followers = user.get("followers", 0)
    except:
        repos = 0
        followers = 0

    # Прогресс-бар
    max_commits = 50
    progress = min(int(commits_today / max_commits * 100), 100) if commits_today > 0 else 5

    # Создаём SVG
    dwg = svgwrite.Drawing("assets/race-stats.svg", size=(800, 220))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=8, fill="#0D1117"))

    # Заголовок
    dwg.add(dwg.text("🏎️ RACE PROGRESS", insert=(400, 30), fill="#FFD700",
                     font_size="18", font_weight="bold", text_anchor="middle", font_family="monospace"))

    # Трасса
    dwg.add(dwg.rect(insert=(50, 60), size=(700, 12), rx=6, fill="#30363D"))
    bar_width = int(700 * progress / 100)
    if bar_width > 0:
        dwg.add(dwg.rect(insert=(50, 60), size=(bar_width, 12), rx=6, fill="#FF4500"))
        # Машинка
        dwg.add(dwg.text("🏎️", insert=(50 + bar_width, 56), font_size="20", text_anchor="middle"))
        dwg.add(dwg.text(f"{progress}%", insert=(50 + bar_width, 46), fill="#FFD700",
                         font_size="14", text_anchor="middle", font_weight="bold", font_family="monospace"))

    # Статистика
    stats = f"Commits today: {commits_today}   |   Repos: {repos}   |   Followers: {followers}"
    dwg.add(dwg.text(stats, insert=(400, 110), fill="#8E9AAF",
                     font_size="14", text_anchor="middle", font_family="monospace"))

    # Финишные флаги
    dwg.add(dwg.text("🏁", insert=(50, 130), font_size="24", text_anchor="middle"))
    dwg.add(dwg.text("🏁", insert=(750, 130), font_size="24", text_anchor="middle"))

    # Подпись
    dwg.add(dwg.text("UPDATED EVERY 8 HOURS VIA GITHUB ACTIONS", insert=(400, 200), fill="#6C7A89",
                     font_size="10", text_anchor="middle", font_family="monospace", font_style="italic"))

    dwg.save()

if __name__ == "__main__":
    create_race_svg()
