from PIL import Image, ImageDraw, ImageFilter
import os
import colorsys

def create_dancer():
    os.makedirs("assets", exist_ok=True)

    width, height = 100, 120
    bg_color = (13, 17, 23)  # #0D1117

    # 8 кадров танца (пиксельные человечки)
    # Каждый кадр — список линий: (x1, y1, x2, y2)
    frames_data = [
        # Кадр 0: стойка прямо
        [
            (50, 10, 50, 70),   # тело
            (50, 30, 30, 50),   # левая рука
            (50, 30, 70, 50),   # правая рука
            (50, 70, 30, 110),  # левая нога
            (50, 70, 70, 110),  # правая нога
        ],
        # Кадр 1: руки вверх
        [
            (50, 10, 50, 70),
            (50, 30, 30, 20),
            (50, 30, 70, 20),
            (50, 70, 30, 110),
            (50, 70, 70, 110),
        ],
        # Кадр 2: правая рука вверх, левая в сторону
        [
            (50, 10, 50, 70),
            (50, 30, 30, 45),
            (50, 30, 70, 20),
            (50, 70, 30, 110),
            (50, 70, 70, 110),
        ],
        # Кадр 3: наклон влево
        [
            (50, 10, 40, 70),
            (45, 35, 25, 50),
            (45, 35, 65, 50),
            (40, 70, 20, 100),
            (40, 70, 60, 100),
        ],
        # Кадр 4: наклон вправо
        [
            (50, 10, 60, 70),
            (55, 35, 35, 50),
            (55, 35, 75, 50),
            (60, 70, 40, 100),
            (60, 70, 80, 100),
        ],
        # Кадр 5: присед
        [
            (50, 10, 50, 60),
            (50, 30, 25, 45),
            (50, 30, 75, 45),
            (50, 60, 35, 100),
            (50, 60, 65, 100),
        ],
        # Кадр 6: левая нога вверх
        [
            (50, 10, 50, 70),
            (50, 30, 30, 50),
            (50, 30, 70, 50),
            (50, 70, 30, 90),
            (50, 70, 70, 95),
        ],
        # Кадр 7: правая нога вверх
        [
            (50, 10, 50, 70),
            (50, 30, 30, 50),
            (50, 30, 70, 50),
            (50, 70, 30, 95),
            (50, 70, 70, 90),
        ],
    ]

    total_frames = 32  # 8 кадров × 4 повторения = плавный цикл
    generated_frames = []

    for i in range(total_frames):
        idx = i % len(frames_data)
        lines = frames_data[idx]

        # Цвет неона: переливается от 0 до 360 по hue
        hue = (i / total_frames) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        neon_color = (int(r * 255), int(g * 255), int(b * 255))

        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img, 'RGBA')

        # Рисуем линии человечка
        for line in lines:
            draw.line(line, fill=neon_color, width=3)

        # Голова
        draw.ellipse((43, 2, 57, 16), outline=neon_color, width=2)

        # Свечение
        blur = img.filter(ImageFilter.GaussianBlur(2))
        img = Image.blend(img, blur, 0.35)

        generated_frames.append(img)

    # Сохраняем GIF
    generated_frames[0].save(
        "assets/dancer.gif",
        save_all=True,
        append_images=generated_frames[1:],
        loop=0,
        duration=80,   # ~12 FPS
        disposal=2
    )

if __name__ == "__main__":
    create_dancer()
