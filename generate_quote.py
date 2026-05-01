import svgwrite
import os
import random

def create_quote_svg(
    quote="Я твой недостаток, ты моя Вселенная",
    author="Баста",
    filename="assets/quote.svg"
):
    os.makedirs("assets", exist_ok=True)

    width, height = 800, 240
    bg_color = "#0D1117"
    quote_gradient_id = "quoteGrad"
    glow_filter_id = "glow"
    particles_count = 30

    # ✅ debug=False отключает строгую проверку SVG-валидатором
    dwg = svgwrite.Drawing(filename, size=(f"{width}px", f"{height}px"), profile='full', debug=False)

    # --- Определения (градиенты, фильтры) ---
    defs = dwg.defs

    # Градиент для текста цитаты (золотой → оранжевый → розовый)
    gradient = dwg.linearGradient(id=quote_gradient_id, x1=0, y1=0, x2=1, y2=0)
    gradient.add_stop_color(offset="0%", color="#FFD700")
    gradient.add_stop_color(offset="50%", color="#FF8C00")
    gradient.add_stop_color(offset="100%", color="#FF1493")
    defs.add(gradient)

    # Фильтр свечения
    glow_filter = dwg.filter(id=glow_filter_id, x="-20%", y="-20%", width="140%", height="140%")
    glow_filter.feGaussianBlur(in_="SourceAlpha", stdDeviation="4", result="blur")
    glow_filter.feFlood(flood_color="#FF4500", flood_opacity="0.8", result="color")
    glow_filter.feComposite(in_="color", in2="blur", operator="in", result="glow")
    
    # ✅ ИСПРАВЛЕНО: feMerge требует список имён слоёв
    glow_filter.feMerge(['glow', 'SourceGraphic'])
    defs.add(glow_filter)

    # --- Фон ---
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill=bg_color, rx=12))

    # --- Частицы (мерцание) ---
    random.seed(42)  # фиксируем расположение для стабильности
    for _ in range(particles_count):
        cx = random.randint(20, width - 20)
        cy = random.randint(20, height - 20)
        r = random.uniform(1.5, 3.5)
        opacity = random.uniform(0.3, 0.8)
        color_choice = random.choice(["#FFD700", "#FF8C00", "#FF1493", "#00FFFF", "#AFEEEE"])
        dwg.add(dwg.circle(center=(cx, cy), r=r, fill=color_choice, opacity=opacity))

    # --- Основная цитата ---
    dwg.add(dwg.text(quote,
                     insert=(width/2, 90),
                     fill=f"url(#{quote_gradient_id})",
                     font_size="32",
                     font_weight="bold",
                     text_anchor="middle",
                     font_family="monospace",
                     filter=f"url(#{glow_filter_id})"))

    # --- Автор ---
    dwg.add(dwg.text(f"— {author}",
                     insert=(width/2, 160),
                     fill="#C9D1D9",
                     font_size="18",
                     text_anchor="middle",
                     font_family="monospace",
                     font_style="italic"))

    # --- Декоративные линии ---
    dwg.add(dwg.line(start=(width/2 - 60, 190), end=(width/2 + 60, 190),
                     stroke="#FF4500", stroke_width=2, opacity=0.8))
    dwg.add(dwg.circle(center=(width/2 - 60, 190), r=3, fill="#FF4500"))
    dwg.add(dwg.circle(center=(width/2 + 60, 190), r=3, fill="#FF4500"))

    dwg.save()
    print(f"✅ SVG успешно создан: {filename}")

if __name__ == "__main__":
    create_quote_svg()
