import svgwrite
import os
import random

def create_max_quote_svg(
    quote="Я твой недостаток, ты моя Вселенная",
    author="Баста",
    filename="assets/max_quote.svg"
):
    os.makedirs("assets", exist_ok=True)

    width, height = 900, 350
    bg_color = "#050505"
    
    # Отключаем строгую валидацию для сложных SVG-фильтров и CSS
    dwg = svgwrite.Drawing(filename, size=(f"{width}px", f"{height}px"), debug=False)

    # ============================================================================
    # 1. CSS СТИЛИ (Анимации и эффекты)
    # ============================================================================
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;700;900&display=swap');

    .bg-orb {
        animation: floatOrb 15s infinite ease-in-out alternate;
        opacity: 0.6;
    }
    .bg-orb:nth-child(2) { animation-delay: -5s; animation-duration: 20s; }
    .bg-orb:nth-child(3) { animation-delay: -10s; animation-duration: 25s; }

    @keyframes floatOrb {
        0%   { transform: translate(0px, 0px) scale(1); }
        33%  { transform: translate(30px, -50px) scale(1.1); }
        66%  { transform: translate(-20px, 20px) scale(0.9); }
        100% { transform: translate(10px, -10px) scale(1.05); }
    }

    .neon-text {
        animation: neonPulse 4s infinite alternate;
        transition: all 0.3s ease;
    }
    .neon-text:hover {
        fill: #FFFFFF !important;
        filter: drop-shadow(0 0 10px #FFFFFF) drop-shadow(0 0 20px #FF0055);
    }

    @keyframes neonPulse {
        0%   { opacity: 0.85; filter: drop-shadow(0 0 5px currentColor); }
        100% { opacity: 1; filter: drop-shadow(0 0 15px currentColor) drop-shadow(0 0 30px currentColor); }
    }

    .particle {
        animation: particleFloat 10s infinite linear;
    }
    @keyframes particleFloat {
        0%   { transform: translateY(0) translateX(0); opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { transform: translateY(-100px) translateX(20px); opacity: 0; }
    }

    .scanlines {
        background: linear-gradient(
            to bottom,
            rgba(255,255,255,0),
            rgba(255,255,255,0) 50%,
            rgba(0,0,0,0.2) 50%,
            rgba(0,0,0,0.2)
        );
        background-size: 100% 4px;
        pointer-events: none;
    }

    .author-text {
        animation: fadeIn 3s ease-out 1s forwards;
        opacity: 0;
    }
    @keyframes fadeIn {
        to { opacity: 0.8; }
    }
    """
    dwg.add(dwg.style(css))

    # ============================================================================
    # 2. ДЕФИНИЦИИ (Градиенты и Фильтры)
    # ============================================================================
    defs = dwg.defs

    # Градиент для текста
    text_grad = dwg.linearGradient(id="textGrad", x1=0, y1=0, x2=1, y2=0)
    text_grad.add_stop_color(offset="0%", color="#FF0055")
    text_grad.add_stop_color(offset="50%", color="#FFD700")
    text_grad.add_stop_color(offset="100%", color="#00FFFF")
    defs.add(text_grad)

    # Градиент для фона
    bg_grad = dwg.radialGradient(id="bgGrad", cx="50%", cy="50%", r="50%")
    bg_grad.add_stop_color(offset="0%", color="#1a0b2e")
    bg_grad.add_stop_color(offset="100%", color="#000000")
    defs.add(bg_grad)

    # Фильтр размытия для фоновых пятен
    blur_filter = dwg.filter(id="heavyBlur", x="-50%", y="-50%", width="200%", height="200%")
    blur_filter.feGaussianBlur(stdDeviation="40")
    defs.add(blur_filter)

    # Паттерн сканлайнов
    pattern = dwg.pattern(id="scanlinePattern", patternUnits="userSpaceOnUse", width="4", height="4")
    pattern.add(dwg.rect(size=(4, 2), fill="#ffffff", opacity=0.03))
    defs.add(pattern)

    # ============================================================================
    # 3. ФОН И АТМОСФЕРА
    # ============================================================================
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="url(#bgGrad)"))

    # Плавающие цветные пятна
    blobs_group = dwg.g(class_="bg-blobs")
    blob_colors = ["#FF0055", "#00FFFF", "#7000FF"]
    for i in range(3):
        circle = dwg.circle(
            center=(width // 2 + (i - 1) * 200, height // 2),
            r=150,
            fill=blob_colors[i],
            filter="url(#heavyBlur)",
            class_="bg-orb"
        )
        blobs_group.add(circle)
    dwg.add(blobs_group)

    # Сканлайны и рамка
    dwg.add(dwg.rect(insert=(0, 0), size=("100%", "100%"), fill="url(#scanlinePattern)"))
    dwg.add(dwg.rect(insert=(15, 15), size=(width - 30, height - 30), 
                     fill="none", stroke="#FFFFFF", stroke_width=1, opacity=0.15, rx=12))

    # ============================================================================
    # 4. ЧАСТИЦЫ
    # ============================================================================
    particles_group = dwg.g()
    random.seed(42)
    for _ in range(45):
        x = random.randint(20, width - 20)
        y = random.randint(20, height - 20)
        size = random.uniform(1, 3)
        delay = random.uniform(0, 12)
        duration = random.uniform(8, 16)
        color = random.choice(["#FF0055", "#00FFFF", "#FFD700", "#FFFFFF"])
        
        circle = dwg.circle(center=(x, y), r=size, fill=color)
        circle.attribs['style'] = f"animation: particleFloat {duration}s linear infinite; animation-delay: -{delay}s;"
        particles_group.add(circle)
    dwg.add(particles_group)

    # ============================================================================
    # 5. ТЕКСТ
    # ============================================================================
    # Цитата
    dwg.add(dwg.text(
        quote,
        insert=(width / 2, height / 2 - 15),
        fill="url(#textGrad)",
        font_size="34",
        font_weight="900",
        text_anchor="middle",
        dominant_baseline="middle",
        font_family="'Montserrat', sans-serif",
        letter_spacing="1px",
        class_="neon-text"
    ))

    # Разделитель
    dwg.add(dwg.line(start=(width/2 - 40, height/2 + 35), end=(width/2 + 40, height/2 + 35), 
                     stroke="#FFFFFF", stroke_width=1.5, opacity=0.6))

    # Автор
    dwg.add(dwg.text(
        f"— {author}",
        insert=(width / 2, height / 2 + 75),
        fill="#FFFFFF",
        font_size="16",
        font_weight="300",
        text_anchor="middle",
        dominant_baseline="middle",
        font_family="'Montserrat', sans-serif",
        letter_spacing="2px",
        class_="author-text"
    ))

    # ============================================================================
    # 6. СОХРАНЕНИЕ
    # ============================================================================
    dwg.save(pretty=True)
    print(f"✅ Готово: {filename}")

if __name__ == "__main__":
    create_max_quote_svg()
