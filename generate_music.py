import svgwrite
import requests
import os
import base64

def download_image(url):
    """Скачивает фото и возвращает base64 для вставки в SVG"""
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return f"data:image/jpeg;base64,{base64.b64encode(r.content).decode()}"
    except:
        pass
    return None

def create_artists_svg():
    os.makedirs("assets", exist_ok=True)

    artists = [
        {
            "name": "Miyagi & Эндшпиль",
            "url": "https://music.yandex.ru/artist/4611844",
            "photo": "https://i.pinimg.com/736x/11/b8/69/11b869004a82ea35a78bdfda6688b68e.jpg",
            "color": "#FF4500"
        },
        {
            "name": "УННВ",
            "url": "https://music.yandex.ru/artist/6766971",
            "photo": "https://i.pinimg.com/736x/a8/8a/fa/a88afaf10f61baa56d2560f78891c049.jpg",
            "color": "#AFEEEE"
        },
        {
            "name": "Баста",
            "url": "https://music.yandex.ru/artist/41191",
            "photo": "https://i.pinimg.com/736x/56/8e/5e/568e5e3fe9cf4ca45e6bcd2718ff6fdc.jpg",
            "color": "#FFD700"
        },
        {
            "name": "ГУФ",
            "url": "https://music.yandex.ru/artist/158454",
            "photo": "https://i.pinimg.com/736x/d6/94/db/d694dbc1414a1431e319264294e16c4a.jpg",
            "color": "#8A2BE2"
        }
    ]

    width = 160 * len(artists) + 40
    height = 220
    dwg = svgwrite.Drawing("assets/artists.svg", size=(f"{width}px", f"{height}px"), profile='full')

    # Фон (под тёмную тему)
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="#0D1117", rx=12))

    # Добавляем определения для свечения
    defs = dwg.defs
    for i, artist in enumerate(artists):
        filter_id = f"glow_{i}"
        glow = dwg.filter(id=filter_id, x="-30%", y="-30%", width="160%", height="160%")

        blur = dwg.feGaussianBlur(in_="SourceAlpha", stdDeviation="6", result="blur")
        glow.add(blur)

        flood = dwg.feFlood(flood_color=artist["color"], flood_opacity="0.8", result="color")
        glow.add(flood)

        composite = dwg.feComposite(in_="color", in2="blur", operator="in", result="glow")
        glow.add(composite)

        merge = dwg.feMerge()
        merge.add(dwg.feMergeNode(in_="glow"))
        merge.add(dwg.feMergeNode(in_="SourceGraphic"))
        glow.add(merge)

        defs.add(glow)

    # Рисуем каждого артиста
    for i, artist in enumerate(artists):
        cx = 100 + i * 160
        cy_logo = 70
        cy_text = 180

        # Внешний светящийся круг
        dwg.add(dwg.circle(center=(cx, cy_logo), r=65, fill="none",
                           stroke=artist["color"], stroke_width=3,
                           filter=f"url(#glow_{i})"))

        # Фото (круг через clip-path)
        clip_id = f"clip_{i}"
        clip = dwg.defs.add(dwg.clipPath(id=clip_id))
        clip.add(dwg.circle(center=(cx, cy_logo), r=62))

        photo_b64 = download_image(artist["photo"])
        if photo_b64:
            dwg.add(dwg.image(href=photo_b64, insert=(cx-62, cy_logo-62),
                              width=124, height=124, clip_path=f"url(#{clip_id})"))
        else:
            dwg.add(dwg.circle(center=(cx, cy_logo), r=62, fill="#30363D",
                               clip_path=f"url(#{clip_id})"))

        # Имя артиста
        dwg.add(dwg.text(artist["name"], insert=(cx, cy_text), fill=artist["color"],
                         font_size="14", font_weight="bold", text_anchor="middle",
                         font_family="monospace", filter=f"url(#glow_{i})"))

    # Бейджи лейблов
    dwg.add(dwg.text("Hajime Records  •  Gazgolder", insert=(width//2, 205),
                     fill="#6C7A89", font_size="10", text_anchor="middle", font_family="monospace"))

    dwg.save()

if __name__ == "__main__":
    create_artists_svg()
