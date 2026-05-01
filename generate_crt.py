import svgwrite, requests, os, random

def create_crt_svg(username="Moty2111"):
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

    dwg = svgwrite.Drawing("assets/crt-stats.svg", size=(400,200))
    dwg.add(dwg.rect(insert=(0,0), size=("100%","100%"), fill="#0D1117", rx=8))
    # линии развёртки
    for y in range(0,200,3):
        dwg.add(dwg.rect(insert=(0,y), size=(400,1), fill="#ffffff", opacity=0.05))
    # текст в стиле терминала
    dwg.add(dwg.text("📺 CRT MONITOR", insert=(200,30), fill="#00FF41", font_size="16", font_weight="bold", text_anchor="middle", font_family="monospace"))
    dwg.add(dwg.text(f"> Repos: {repos}", insert=(40,60), fill="#00FF41", font_size="11", font_family="monospace"))
    dwg.add(dwg.text(f"> Followers: {followers}", insert=(40,82), fill="#00FF41", font_size="11", font_family="monospace"))
    dwg.add(dwg.text(f"> Recent commits: {commits}", insert=(40,104), fill="#00FF41", font_size="11", font_family="monospace"))
    dwg.add(dwg.text("> STATUS: ONLINE", insert=(40,126), fill="#00FF41", font_size="11", font_family="monospace"))
    dwg.add(dwg.text("UPDATED EVERY 8 HOURS", insert=(200,170), fill="#006600", font_size="8", text_anchor="middle"))
    dwg.save()

if __name__=="__main__":
    create_crt_svg()
