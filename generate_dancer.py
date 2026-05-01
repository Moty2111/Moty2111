from PIL import Image, ImageDraw, ImageFilter
import os, math, random

def create_dancer():
    os.makedirs("assets", exist_ok=True)
    frames = []
    width, height = 200, 300
    # позы танцующего человечка (простая стик-фигура)
    poses = [
        # (x1,y1,x2,y2) для туловища, рук, ног
        # нейтрально
        {"body":(100,50,100,180), "l_arm":(100,100,60,140), "r_arm":(100,100,140,60), "l_leg":(100,180,70,260), "r_leg":(100,180,130,260)},
        # руки вверх
        {"body":(100,50,100,180), "l_arm":(100,100,60,80), "r_arm":(100,100,140,80), "l_leg":(100,180,70,260), "r_leg":(100,180,130,260)},
        # руки в стороны
        {"body":(100,50,100,180), "l_arm":(100,100,40,120), "r_arm":(100,100,160,120), "l_leg":(100,180,70,240), "r_leg":(100,180,130,240)},
        # одна нога вверх
        {"body":(100,50,100,180), "l_arm":(100,100,60,120), "r_arm":(100,100,140,140), "l_leg":(100,180,60,200), "r_leg":(100,180,140,220)},
        # присед
        {"body":(100,50,100,160), "l_arm":(100,90,60,130), "r_arm":(100,90,140,130), "l_leg":(100,160,90,240), "r_leg":(100,160,110,240)},
    ]
    neon_color = (0, 255, 255)  # циан
    glow_color = (0, 180, 180)
    bg_color = (13, 17, 23)  # #0D1117

    for i in range(24):  # 24 кадра для плавности
        pose_idx = i % len(poses)
        pose = poses[pose_idx]
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        # тело (линия)
        draw.line([pose["body"][:2], pose["body"][2:]], fill=neon_color, width=4)
        # руки
        draw.line([pose["l_arm"][:2], pose["l_arm"][2:]], fill=neon_color, width=4)
        draw.line([pose["r_arm"][:2], pose["r_arm"][2:]], fill=neon_color, width=4)
        # ноги
        draw.line([pose["l_leg"][:2], pose["l_leg"][2:]], fill=neon_color, width=4)
        draw.line([pose["r_leg"][:2], pose["r_leg"][2:]], fill=neon_color, width=4)
        # голова (окружность)
        draw.ellipse((80, 20, 120, 60), outline=neon_color, width=3)
        # эффект свечения: размытая копия
        blur = img.filter(ImageFilter.GaussianBlur(3))
        # накладываем размытую версию для свечения
        img = Image.blend(img, blur, 0.5)
        frames.append(img)

    frames[0].save("assets/dancer.gif", save_all=True, append_images=frames[1:], loop=0, duration=100, disposal=2)

if __name__ == "__main__":
    create_dancer()
