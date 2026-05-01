from PIL import Image, ImageDraw, ImageFilter
import os
import math
import colorsys

def create_dancer():
    os.makedirs("assets", exist_ok=True)

    width, height = 200, 300
    bg_color = (13, 17, 23)          # #0D1117

    # Базовые позы (ключевые кадры)
    poses = [
        {  # стойка прямо
            "body": (100, 50, 100, 180),
            "left_arm": (100, 100, 60, 140),
            "right_arm": (100, 100, 140, 60),
            "left_leg": (100, 180, 70, 260),
            "right_leg": (100, 180, 130, 260)
        },
        {  # руки вверх
            "body": (100, 50, 100, 180),
            "left_arm": (100, 100, 60, 80),
            "right_arm": (100, 100, 140, 80),
            "left_leg": (100, 180, 70, 260),
            "right_leg": (100, 180, 130, 260)
        },
        {  # руки в стороны
            "body": (100, 50, 100, 180),
            "left_arm": (100, 100, 40, 120),
            "right_arm": (100, 100, 160, 120),
            "left_leg": (100, 180, 70, 240),
            "right_leg": (100, 180, 130, 240)
        },
        {  # одна нога вверх
            "body": (100, 50, 100, 180),
            "left_arm": (100, 100, 60, 120),
            "right_arm": (100, 100, 140, 140),
            "left_leg": (100, 180, 60, 200),
            "right_leg": (100, 180, 140, 220)
        },
        {  # присед
            "body": (100, 50, 100, 160),
            "left_arm": (100, 90, 60, 130),
            "right_arm": (100, 90, 140, 130),
            "left_leg": (100, 160, 90, 240),
            "right_leg": (100, 160, 110, 240)
        }
    ]

    total_frames = 48          # количество кадров для плавности
    frames = []
    num_poses = len(poses)

    for i in range(total_frames):
        # определим две соседние позы и долю смешения (0..1)
        idx = i % num_poses
        next_idx = (idx + 1) % num_poses
        t = (i % (total_frames // num_poses)) / (total_frames // num_poses)

        pose1 = poses[idx]
        pose2 = poses[next_idx]

        # интерполяция между двумя позами
        current_pose = {}
        for part in ["body", "left_arm", "right_arm", "left_leg", "right_leg"]:
            x1, y1, x2, y2 = pose1[part]
            x1_next, y1_next, x2_next, y2_next = pose2[part]
            current_pose[part] = (
                int(x1 + (x1_next - x1) * t),
                int(y1 + (y1_next - y1) * t),
                int(x2 + (x2_next - x2) * t),
                int(y2 + (y2_next - y2) * t)
            )

        # цвет неона: циклический сдвиг оттенка
        hue = (i / total_frames) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        neon_color = (int(r * 255), int(g * 255), int(b * 255))

        # создаём кадр
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img, 'RGBA')

        # туловище
        draw.line(current_pose["body"], fill=neon_color, width=4)
        # левая рука
        draw.line(current_pose["left_arm"], fill=neon_color, width=4)
        # правая рука
        draw.line(current_pose["right_arm"], fill=neon_color, width=4)
        # левая нога
        draw.line(current_pose["left_leg"], fill=neon_color, width=4)
        # правая нога
        draw.line(current_pose["right_leg"], fill=neon_color, width=4)
        # голова
        draw.ellipse((85, 20, 115, 50), outline=neon_color, width=3)

        # свечение (размытая копия)
        blur = img.filter(ImageFilter.GaussianBlur(3))
        img = Image.blend(img, blur, 0.4)

        frames.append(img)

    # сохраняем анимированный GIF
    duration = int(100 / (total_frames / num_poses))  # примерно 100 мс на ключевую позу
    frames[0].save(
        "assets/dancer.gif",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=100,       # фиксированная задержка 100 мс между кадрами
        disposal=2
    )

if __name__ == "__main__":
    create_dancer()
