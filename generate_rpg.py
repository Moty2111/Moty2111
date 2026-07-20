import svgwrite
import requests
import os

def create_rpg_svg(username="Moty2111"):
    os.makedirs("assets", exist_ok=True)
    headers = {"Accept": "application/vnd.github.v3+json"}
    repos = followers = commits = 0
    
    # Получаем базовую информацию о пользователе
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        if r.status_code == 200:
            u = r.json()
            repos = u.get("public_repos", 0)
            followers = u.get("followers", 0)
    except Exception:
        pass
        
    # Получаем информацию о последних событиях (коммитах)
    try:
        r2 = requests.get(f"https://api.github.com/users/{username}/events/public", headers=headers, timeout=10)
        if r2.status_code == 200:
            events = r2.json()
            commits = sum(1 for e in events if e.get("type") == "PushEvent")
    except Exception:
        pass

    # Инициализация SVG
    dwg = svgwrite.Drawing("assets/rpg-stats.svg", size=(420, 220), profile='tiny')
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="#0D1117", rx=10))
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="none", stroke="#FFD700", stroke_width=2, rx=10))
    dwg.add(dwg.text("🎮 RPG CHARACTER", insert=(210, 30), fill="#FFD700", font_size="18", font_weight="bold",
                     text_anchor="middle", font_family="monospace"))
    
    stats = [
        ("⚔️ Strength", min(commits * 2, 100)),
        ("🛡️ Defense", min(repos * 5, 100)),
        ("💡 Intelligence", min(followers * 10, 100)),
        ("❤️ Health", 100)
    ]
    
    y = 65
    for label, val in stats:
        # Название характеристики (выровнено по правому краю для аккуратности перед полосой)
        dwg.add(dwg.text(label, insert=(170, y), fill="#FFFFFF", font_size="14", font_family="monospace", text_anchor="end"))
        
        # Фон полосы прогресса
        dwg.add(dwg.rect(insert=(180, y - 10), size=(160, 12), rx=4, fill="#30363D"))
        
        # Заполнение полосы прогресса
        bar_w = int(160 * val / 100)
        if bar_w > 0:
            # Более чистый и надежный способ генерации HEX-цвета
            r_val = int(255 - (255 * val / 100))
            g_val = int(100 + (155 * val / 100))
            color = f"#{r_val:02x}{g_val:02x}00" if val < 100 else "#58A6FF"
            dwg.add(dwg.rect(insert=(180, y - 10), size=(bar_w, 12), rx=4, fill=color))
            
        # Числовое значение справа
        dwg.add(dwg.text(str(val), insert=(350, y), fill="#FFFFFF", font_size="12", text_anchor="middle",
                         font_family="monospace"))
        y += 32
        
    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(210, 200), fill="#6C7A89", font_size="10",
                     text_anchor="middle", font_family="monospace"))
    dwg.save()

if __name__ == "__main__":
    create_rpg_svg()
