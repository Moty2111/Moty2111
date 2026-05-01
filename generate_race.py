import svgwrite
import requests
import math
from datetime import datetime, timedelta

def create_race_svg(username="Moty2111"):
    # Получаем данные из GitHub API
    url = f"https://api.github.com/users/{username}/events/public"
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        events = r.json()
        commits = sum(1 for e in events if e.get("type") == "PushEvent")
    except:
        commits = 0

    # Получаем общее число коммитов (приблизительно)
    try:
        r2 = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        user_data = r2.json()
        total_repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)
    except:
        total_repos = 0
        followers = 0

    # Прогресс за день (максимум 50 коммитов для шкалы)
    progress = min(int(commits / 50 * 100), 100) if commits > 0 else 5

    dwg = svgwrite.Drawing("assets/race-stats.svg", size=(800, 220))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), rx=8, fill="#0D1117"))

    # Название
    dwg.add(dwg.text("🏎️ RACE PROGRESS", insert=(400, 30), fill="#FFD700",
                     font_size="18", font_weight="bold", text_anchor="middle", font_family="monospace"))

    # Трасса (линия)
    dwg.add(dwg.rect(insert=(50, 60), size=(700, 12), rx=6, fill="#30363D"))
    # Прогресс
    bar_width = int(700 * progress / 100)
    if bar_width > 0:
        dwg.add(dwg.rect(insert=(50, 60), size=(bar_width, 12), rx=6, fill="#FF4500"))
        dwg.add(dwg.circle(center=(50 + bar_width, 66), r=8, fill="#FFD700"))
        # Машинка (эмодзи или примитив)
        dwg.add(dwg.text("🏎️", insert=(50 + bar_width, 56), font_size="20", text_anchor="middle"))

    # Проценты
    dwg.add(dwg.text(f"{progress}%", insert=(50 + bar_width, 48), fill="#FFD700",
                     font_size="14", text_anchor="middle", font_weight="bold", font_family="monospace"))

    # Статистика снизу
    stats_text = f"Commits today: {commits}   |   Repos: {total_repos}   |   Followers: {followers}"
    dwg.add(dwg.text(stats_text, insert=(400, 110), fill="#8E9AAF",
                     font_size="14", text_anchor="middle", font_family="monospace"))

    # Декоративные элементы (финишные флаги)
    dwg.add(dwg.text("🏁", insert=(50, 130), font_size="24", text_anchor="middle"))
    dwg.add(dwg.text("🏁", insert=(750, 130), font_size="24", text_anchor="middle"))

    # Подпись
    dwg.add(dwg.text("UPDATED DAILY VIA GITHUB ACTIONS", insert=(400, 200), fill="#6C7A89",
                     font_size="10", text_anchor="middle", font_family="monospace"))

    dwg.save()

if __name__ == "__main__":
    create_race_svg()
