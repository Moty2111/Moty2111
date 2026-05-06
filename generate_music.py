import svgwrite, requests, os, base64
from svgwrite.filters import Filter, feGaussianBlur, feFlood, feComposite, feMerge, feMergeNode

def download_image(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        r = requests.get(url, timeout=15, headers=headers)
        if r.status_code == 200:
            return f"data:image/jpeg;base64,{base64.b64encode(r.content).decode()}"
    except:
        pass
    return None

def create_artists_svg():
    os.makedirs("assets", exist_ok=True)

    artists = [
        {"name": "Miyagi & Эндшпиль", "color": "#FF4500",
         "photo": "https://i.pinimg.com/736x/11/b8/69/11b869004a82ea35a78bdfda6688b68e.jpg"},
        {"name": "УННВ", "color": "#AFEEEE",
         "photo": "https://i.pinimg.com/736x/a8/8a/fa/a88afaf10f61baa56d2560f78891c049.jpg"},
        {"name": "Баста", "color": "#FFD700",
         "photo": "https://i.pinimg.com/736x/56/8e/5e/568e5e3fe9cf4ca45e6bcd2718ff6fdc.jpg"},
        {"name": "ГУФ", "color": "#8A2BE2",
         "photo": "https://i.pinimg.com/736x/d6/94/db/d694dbc1414a1431e319264294e16c4a.jpg"},
    ]

    width = 160 * len(artists) + 40
    height = 220
    dwg = svgwrite.Drawing("assets/artists.svg", size=(f"{width}px", f"{height}px"), profile='full')
    dwg.add(dwg.rect(insert=(0,0), size=("100%","100%"), fill="#0D1117", rx=12))

    defs = dwg.defs

    for i, artist in enumerate(artists):
        fil = Filter(id=f"glow_{i}", x="-50%", y="-50%", width="200%", height="200%")
        fil.add(feGaussianBlur(in_="SourceAlpha", stdDeviation="6", result="blur"))
        fil.add(feFlood(flood_color=artist["color"], flood_opacity="0.8", result="color"))
        fil.add(feComposite(in_="color", in2="blur", operator="in", result="glow"))
        merge = feMerge()
        merge.add(feMergeNode(in_="glow"))
        merge.add(feMergeNode(in_="SourceGraphic"))
        fil.add(merge)
        defs.add(fil)

    for i, artist in enumerate(artists):
        cx = 100 + i * 160
        cy_logo = 70
        cy_text = 180

        # Неоновый круг
        dwg.add(dwg.circle(center=(cx, cy_logo), r=65, fill="none",
                           stroke=artist["color"], stroke_width=3, filter=f"url(#glow_{i})"))

        # Круглая маска
        clip_id = f"clip_{i}"
        clip = dwg.clipPath(id=clip_id)
        clip.add(dwg.circle(center=(cx, cy_logo), r=62))
        defs.add(clip)

        photo_b64 = download_image(artist["photo"])
        if photo_b64:
            dwg.add(dwg.image(href=photo_b64, insert=(cx-62, cy_logo-62),
                              width=124, height=124,
                              clip_path=f"url(#{clip_id})",
                              preserveAspectRatio="xMidYMid slice"))
        else:
            dwg.add(dwg.circle(center=(cx, cy_logo), r=62, fill="#30363D",
                               clip_path=f"url(#{clip_id})"))

        dwg.add(dwg.text(artist["name"], insert=(cx, cy_text), fill=artist["color"],
                         font_size="14", font_weight="bold", text_anchor="middle",
                         font_family="monospace", filter=f"url(#glow_{i})"))

    dwg.add(dwg.text("Hajime Records  •  Gazgolder", insert=(width//2, 205),
                     fill="#6C7A89", font_size="10", text_anchor="middle", font_family="monospace"))

    dwg.save()

if __name__ == "__main__":
    create_artists_svg()
