import svgwrite, requests, os, random

def create_race_svg(username="Moty2111"):
    os.makedirs("assets", exist_ok=True)
    headers = {"Accept": "application/vnd.github.v3+json"}
    commits = repos = followers = 0
    try:
        r = requests.get(f"https://api.github.com/users/{username}/events/public", headers=headers, timeout=10)
        if r.status_code==200:
            events = r.json()
            commits = sum(1 for e in events if e.get("type")=="PushEvent")
    except: pass
    try:
        r2 = requests.get(f"https://api.github.com/users/{username}", headers=headers, timeout=10)
        if r2.status_code==200:
            u = r2.json()
            repos = u.get("public_repos",0)
            followers = u.get("followers",0)
    except: pass

    max_commits = 50
    progress = min(int(commits/max_commits*100), 100) if commits>0 else 5
    dwg = svgwrite.Drawing("assets/race-stats.svg", size=(800, 220))
    # фон с сеткой
    dwg.add(dwg.rect(insert=(0,0), size=("100%","100%"), fill="#0D1117", rx=10))
    for i in range(0,800,20):
        dwg.add(dwg.line(start=(i,0), end=(i,220), stroke="#30363D", stroke_width=0.5, opacity=0.3))
    # Заголовок
    dwg.add(dwg.text("🏎️ RACE PROGRESS", insert=(400,35), fill="url(#neonGrad)", font_size="20", font_weight="bold", text_anchor="middle", font_family="monospace"))
    # Градиент для текста (заглушка, в svgwrite сложно)
    # Трасса
    dwg.add(dwg.rect(insert=(50,70), size=(700,14), rx=7, fill="#30363D"))
    bar_w = int(700*progress/100)
    if bar_w>0:
        # градиентная полоса
        dwg.add(dwg.rect(insert=(50,70), size=(bar_w,14), rx=7, fill="#FF4500"))
        # машинка
        dwg.add(dwg.text("🏎️", insert=(50+bar_w,62), font_size="22", text_anchor="middle"))
        dwg.add(dwg.text(f"{progress}%", insert=(50+bar_w,52), fill="#FFD700", font_size="14", text_anchor="middle", font_weight="bold"))
    # Статистика
    stats = f"Commits: {commits}   |   Repos: {repos}   |   Followers: {followers}"
    dwg.add(dwg.text(stats, insert=(400,130), fill="#8E9AAF", font_size="14", text_anchor="middle"))
    # Финиш
    dwg.add(dwg.text("🏁", insert=(50,160), font_size="24", text_anchor="middle"))
    dwg.add(dwg.text("🏁", insert=(750,160), font_size="24", text_anchor="middle"))
    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(400,200), fill="#6C7A89", font_size="9", text_anchor="middle", font_style="italic"))
    dwg.save()

if __name__=="__main__":
    create_race_svg()
