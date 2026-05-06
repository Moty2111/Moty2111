import svgwrite, requests, os

def create_rpg_svg(username="Moty2111"):
    os.makedirs("assets", exist_ok=True)
    headers = {"Accept": "application/vnd.github.v3+json"}
    repos=followers=commits=0
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        if r.status_code==200:
            u = r.json()
            repos = u.get("public_repos",0)
            followers = u.get("followers",0)
    except: pass
    try:
        r2 = requests.get(f"https://api.github.com/users/{username}/events/public", headers=headers, timeout=10)
        if r2.status_code==200:
            events = r2.json()
            commits = sum(1 for e in events if e.get("type")=="PushEvent")
    except: pass

    dwg = svgwrite.Drawing("assets/rpg-stats.svg", size=(420,240))
    dwg.add(dwg.rect(insert=(0,0), size=("100%","100%"), fill="#0D1117", rx=10))
    dwg.add(dwg.rect(insert=(0,0), size=("100%","100%"), fill="none", stroke="#FFD700", stroke_width=2, rx=10))
    # Заголовок крупнее
    dwg.add(dwg.text("🎮 RPG CHARACTER", insert=(210,35), fill="#FFD700", font_size="20", font_weight="bold", text_anchor="middle", font_family="monospace"))

    stats = [
        ("⚔️ Strength", min(commits*2,100)),
        ("🛡️ Defense", min(repos*5,100)),
        ("💡 Intelligence", min(followers*10,100)),
        ("❤️ Health", 100)
    ]
    y=75
    for label, val in stats:
        # Название характеристики крупнее
        dwg.add(dwg.text(label, insert=(100, y), fill="#FFFFFF", font_size="16", font_family="monospace"))
        # Полоса прогресса
        dwg.add(dwg.rect(insert=(200, y-12), size=(180,14), rx=5, fill="#30363D"))
        bar_w = int(180*val/100)
        if bar_w>0:
            color = f"#{hex(255-int(255*val/100))[2:].zfill(2)}{hex(100+int(155*val/100))[2:].zfill(2)}00" if val<100 else "#58A6FF"
            dwg.add(dwg.rect(insert=(200, y-12), size=(bar_w,14), rx=5, fill=color))
        # Значение крупнее
        dwg.add(dwg.text(str(val), insert=(390, y), fill="#FFFFFF", font_size="14", text_anchor="middle", font_family="monospace"))
        y += 32
    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(210,215), fill="#6C7A89", font_size="9", text_anchor="middle"))
    dwg.save()

if __name__=="__main__":
    create_rpg_svg()
