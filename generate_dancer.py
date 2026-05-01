from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
import colorsys
import math
import random

# ============================================================================
# 🎨 ЦВЕТОВЫЕ ПАЛИТРЫ И УТИЛИТЫ
# ============================================================================

class ColorPalette:
    """Гармоничные цветовые схемы для неон-эффектов"""
    PALETTES = {
        'cyberpunk': [(255, 0, 255), (0, 255, 255), (255, 100, 0), (100, 255, 0)],
        'sunset':    [(255, 100, 200), (255, 150, 50), (100, 200, 255), (200, 100, 255)],
        'ocean':     [(0, 200, 255), (0, 100, 200), (100, 255, 200), (0, 255, 150)],
        'fire':      [(255, 50, 0), (255, 150, 0), (255, 200, 100), (255, 255, 200)],
        'matrix':    [(0, 255, 100), (0, 200, 50), (100, 255, 150), (0, 255, 200)],
    }
    
    @staticmethod
    def get_color(palette_name, t, brightness=1.0):
        colors = ColorPalette.PALETTES.get(palette_name, ColorPalette.PALETTES['cyberpunk'])
        idx = int(t * len(colors)) % len(colors)
        next_idx = (idx + 1) % len(colors)
        local_t = (t * len(colors)) % 1.0
        r = int(lerp(colors[idx][0], colors[next_idx][0], local_t) * brightness)
        g = int(lerp(colors[idx][1], colors[next_idx][1], local_t) * brightness)
        b = int(lerp(colors[idx][2], colors[next_idx][2], local_t) * brightness)
        return (r, g, b)

def lerp(a, b, t):
    """Линейная интерполяция"""
    return a + (b - a) * t

def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))

# ============================================================================
# 🎭 EASING FUNCTIONS — МАТЕМАТИКА ПЛАВНОСТИ
# ============================================================================

class Easing:
    @staticmethod
    def linear(t): 
        return t
    
    @staticmethod
    def ease_in_quad(t): 
        return t * t
    
    @staticmethod
    def ease_out_quad(t): 
        return 1 - (1 - t) * (1 - t)
    
    @staticmethod
    def ease_in_out_quad(t): 
        return t * t * (3 - 2 * t)
    
    @staticmethod
    def ease_in_cubic(t): 
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t): 
        return 1 - (1 - t) ** 3
    
    @staticmethod
    def ease_in_out_cubic(t):
        return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
    
    @staticmethod
    def ease_out_elastic(t):
        if t == 0: 
            return 0
        if t == 1: 
            return 1
        p = 0.3
        return (2 ** (-10 * t) * math.sin((t - p/4) * (2*math.pi) / p) + 1)
    
    @staticmethod
    def ease_out_bounce(t):
        """Исправленная функция без синтаксических ошибок"""
        n1 = 7.5625
        d1 = 2.75
        if t < 1/d1:
            return n1 * t * t
        elif t < 2/d1:
            t_adj = t - 1.5/d1  # ✅ Исправлено: выносим вычитание в переменную
            return n1 * t_adj * t_adj + 0.75
        elif t < 2.5/d1:
            t_adj = t - 2.25/d1  # ✅ Исправлено
            return n1 * t_adj * t_adj + 0.9375
        else:
            t_adj = t - 2.625/d1  # ✅ Исправлено
            return n1 * t_adj * t_adj + 0.984375
    
    @staticmethod
    def smoothstep(t): 
        return t * t * (3 - 2 * t)
    
    @staticmethod
    def smootherstep(t): 
        return t * t * t * (t * (t * 6 - 15) + 10)

# ============================================================================
# 🦴 ПРОЦЕДУРНЫЙ СКЕЛЕТ
# ============================================================================

class Bone:
    """Кость скелета с длиной и углом"""
    def __init__(self, length, angle=0):
        self.length = length
        self.angle = angle
    
    def get_end(self, start_x, start_y):
        return (
            start_x + self.length * math.cos(self.angle),
            start_y + self.length * math.sin(self.angle)
        )

class Skeleton:
    """Процедурный скелет танцора"""
    def __init__(self, cx, cy, scale=1.0):
        self.cx, self.cy = cx, cy
        self.scale = scale
        
        self.spine = Bone(50 * scale)
        self.neck = Bone(15 * scale)
        self.head_r = 12 * scale
        
        self.l_shoulder = Bone(20 * scale)
        self.r_shoulder = Bone(20 * scale)
        self.l_upper_arm = Bone(25 * scale)
        self.r_upper_arm = Bone(25 * scale)
        self.l_lower_arm = Bone(20 * scale)
        self.r_lower_arm = Bone(20 * scale)
        
        self.l_hip = Bone(10 * scale)
        self.r_hip = Bone(10 * scale)
        self.l_upper_leg = Bone(35 * scale)
        self.r_upper_leg = Bone(35 * scale)
        self.l_lower_leg = Bone(30 * scale)
        self.r_lower_leg = Bone(30 * scale)
        
        self.reset_pose()
    
    def reset_pose(self):
        """Исходная Т-поза"""
        self.spine.angle = -math.pi/2
        self.neck.angle = -math.pi/2
        self.l_shoulder.angle = math.pi
        self.r_shoulder.angle = 0
        self.l_upper_arm.angle = math.pi/2
        self.r_upper_arm.angle = math.pi/2
        self.l_lower_arm.angle = math.pi/2
        self.r_lower_arm.angle = math.pi/2
        self.l_hip.angle = -math.pi/2
        self.r_hip.angle = -math.pi/2
        self.l_upper_leg.angle = -math.pi/2
        self.r_upper_leg.angle = -math.pi/2
        self.l_lower_leg.angle = -math.pi/2
        self.r_lower_leg.angle = -math.pi/2
    
    def set_pose(self, pose_data, t=0):
        """Применяет позу с интерполяцией"""
        for bone_name, target_angle in pose_data.items():
            if hasattr(self, bone_name):
                bone = getattr(self, bone_name)
                current = bone.angle
                diff = target_angle - current
                while diff > math.pi: 
                    diff -= 2*math.pi
                while diff < -math.pi: 
                    diff += 2*math.pi
                bone.angle = current + diff * Easing.ease_out_quad(t)
    
    def get_segments(self):
        """Возвращает список отрезков для отрисовки"""
        segments = []
        
        pelvis = (self.cx, self.cy)
        chest = self.spine.get_end(*pelvis)
        neck_base = self.neck.get_end(*chest)
        head_center = (neck_base[0], neck_base[1] - self.head_r)
        
        segments.append((*pelvis, *chest))
        segments.append((*chest, *neck_base))
        
        # Руки
        l_shoulder_end = self.l_shoulder.get_end(*chest)
        l_elbow = self.l_upper_arm.get_end(*l_shoulder_end)
        l_hand = self.l_lower_arm.get_end(*l_elbow)
        segments.append((l_shoulder_end[0], l_shoulder_end[1], l_elbow[0], l_elbow[1]))
        segments.append((l_elbow[0], l_elbow[1], l_hand[0], l_hand[1]))
        
        r_shoulder_end = self.r_shoulder.get_end(*chest)
        r_elbow = self.r_upper_arm.get_end(*r_shoulder_end)
        r_hand = self.r_lower_arm.get_end(*r_elbow)
        segments.append((r_shoulder_end[0], r_shoulder_end[1], r_elbow[0], r_elbow[1]))
        segments.append((r_elbow[0], r_elbow[1], r_hand[0], r_hand[1]))
        
        # Ноги
        l_hip_end = self.l_hip.get_end(*pelvis)
        l_knee = self.l_upper_leg.get_end(*l_hip_end)
        l_foot = self.l_lower_leg.get_end(*l_knee)
        segments.append((l_hip_end[0], l_hip_end[1], l_knee[0], l_knee[1]))
        segments.append((l_knee[0], l_knee[1], l_foot[0], l_foot[1]))
        
        r_hip_end = self.r_hip.get_end(*pelvis)
        r_knee = self.r_upper_leg.get_end(*r_hip_end)
        r_foot = self.r_lower_leg.get_end(*r_knee)
        segments.append((r_hip_end[0], r_hip_end[1], r_knee[0], r_knee[1]))
        segments.append((r_knee[0], r_knee[1], r_foot[0], r_foot[1]))
        
        return segments, head_center, pelvis

# ============================================================================
# 🎵 ХОРЕОГРАФИЯ
# ============================================================================

class Choreography:
    @staticmethod
    def idle(t):
        sway = math.sin(t * 2) * 0.1
        return {
            'spine': -math.pi/2 + sway * 0.1,
            'l_upper_arm': math.pi/2 + math.sin(t * 3) * 0.15,
            'r_upper_arm': math.pi/2 + math.sin(t * 3 + 1) * 0.15,
            'l_lower_arm': math.pi/2 + math.sin(t * 4) * 0.2,
            'r_lower_arm': math.pi/2 + math.sin(t * 4 + 0.5) * 0.2,
        }
    
    @staticmethod
    def wave(t):
        phase = t * 2 * math.pi
        return {
            'spine': -math.pi/2 + math.sin(phase * 0.5) * 0.1,
            'l_shoulder': math.pi + math.sin(phase) * 0.3,
            'r_shoulder': 0 + math.sin(phase + math.pi) * 0.3,
            'l_upper_arm': math.pi/2 + math.sin(phase * 2) * 0.5,
            'r_upper_arm': math.pi/2 + math.sin(phase * 2 + math.pi) * 0.5,
            'l_lower_arm': math.pi/2 + math.sin(phase * 3) * 0.8,
            'r_lower_arm': math.pi/2 + math.sin(phase * 3 + math.pi) * 0.8,
        }
    
    @staticmethod
    def jump(t):
        if t < 0.3:
            progress = t / 0.3
            return {
                'spine': -math.pi/2 + Easing.ease_in_quad(progress) * 0.2,
                'l_upper_leg': -math.pi/2 + Easing.ease_in_quad(progress) * 0.4,
                'r_upper_leg': -math.pi/2 + Easing.ease_in_quad(progress) * 0.4,
                'l_lower_leg': -math.pi/2 + Easing.ease_in_quad(progress) * 0.3,
                'r_lower_leg': -math.pi/2 + Easing.ease_in_quad(progress) * 0.3,
            }
        elif t < 0.7:
            progress = (t - 0.3) / 0.4
            return {
                'spine': -math.pi/2 - Easing.ease_out_quad(progress) * 0.15,
                'l_shoulder': math.pi + Easing.ease_out_quad(progress) * 0.5,
                'r_shoulder': 0 - Easing.ease_out_quad(progress) * 0.5,
                'l_upper_arm': math.pi/2 - Easing.ease_out_quad(progress) * 0.8,
                'r_upper_arm': math.pi/2 - Easing.ease_out_quad(progress) * 0.8,
                'l_upper_leg': -math.pi/2 + Easing.ease_out_quad(progress) * 0.6,
                'r_upper_leg': -math.pi/2 - Easing.ease_out_quad(progress) * 0.6,
            }
        else:
            progress = (t - 0.7) / 0.3
            return {
                'spine': -math.pi/2 + Easing.ease_out_bounce(progress) * 0.1,
                'l_upper_leg': -math.pi/2 + Easing.ease_out_bounce(progress) * 0.2,
                'r_upper_leg': -math.pi/2 + Easing.ease_out_bounce(progress) * 0.2,
            }
    
    @staticmethod
    def spin(t):
        rotation = t * 4 * math.pi
        return {
            'spine': -math.pi/2,
            'l_shoulder': math.pi + math.sin(rotation) * 0.2,
            'r_shoulder': 0 + math.sin(rotation + math.pi) * 0.2,
            'l_upper_arm': math.pi/2 + math.sin(rotation * 2) * 0.4,
            'r_upper_arm': math.pi/2 + math.sin(rotation * 2 + math.pi) * 0.4,
            'l_upper_leg': -math.pi/2 + math.sin(rotation * 1.5) * 0.3,
            'r_upper_leg': -math.pi/2 + math.sin(rotation * 1.5 + math.pi) * 0.3,
        }
    
    @staticmethod
    def hip_hop(t):
        bounce = math.sin(t * 8 * math.pi) * 0.1
        return {
            'spine': -math.pi/2 + bounce,
            'l_hip': -math.pi/2 + math.sin(t * 4) * 0.2,
            'r_hip': -math.pi/2 + math.sin(t * 4 + math.pi) * 0.2,
            'l_upper_arm': math.pi/2 + math.sin(t * 6) * 0.3,
            'r_upper_arm': math.pi/2 + math.sin(t * 6 + math.pi) * 0.3,
            'l_lower_arm': math.pi/2 + math.sin(t * 10) * 0.5,
            'r_lower_arm': math.pi/2 + math.sin(t * 10 + math.pi) * 0.5,
        }

# ============================================================================
# ✨ ВИЗУАЛЬНЫЕ ЭФФЕКТЫ
# ============================================================================

class Particle:
    def __init__(self, x, y, color, life, size, vx, vy):
        self.x, self.y = x, y
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.vx, self.vy = vx, vy
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vy += 0.1
    
    def draw(self, draw):
        if self.life <= 0: 
            return
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha)
        r = self.size * (self.life / self.max_life)
        draw.ellipse(
            (self.x - r, self.y - r, self.x + r, self.y + r),
            fill=color, outline=color
        )
    
    def is_alive(self):
        return self.life > 0

class VisualEffects:
    @staticmethod
    def draw_neon_glow(draw, segments, color, intensity=3):
        for width, opacity in [(intensity*4, 0.1), (intensity*2, 0.3), (intensity, 0.7)]:
            for x1, y1, x2, y2 in segments:
                draw.line((x1, y1, x2, y2), fill=(*color, int(255*opacity)), width=width)
    
    @staticmethod
    def draw_motion_trail(draw, prev_segments, color, alpha=80):
        for x1, y1, x2, y2 in prev_segments:
            draw.line((x1, y1, x2, y2), fill=(*color, alpha), width=3)
    
    @staticmethod
    def draw_sparkles(draw, particles):
        for p in particles:
            p.draw(draw)
    
    @staticmethod
    def apply_screen_shake(img, intensity, frame_idx):
        if intensity <= 0:
            return img
        offset_x = int(math.sin(frame_idx * 0.5) * intensity)
        offset_y = int(math.cos(frame_idx * 0.7) * intensity)
        result = Image.new('RGB', img.size, (0, 0, 0))
        result.paste(img, (offset_x, offset_y))
        return result
    
    @staticmethod
    def draw_background(draw, width, height, t, palette_name='cyberpunk'):
        for y in range(height):
            hue = (t * 0.3 + y / height * 0.2) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.15, 0.1)
            draw.line([(0, y), (width, y)], fill=(int(r*255), int(g*255), int(b*255)))
        
        grid_color = ColorPalette.get_color(palette_name, t, 0.3)
        for x in range(0, width, 40):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, 40):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
        
        for i in range(3):
            radius = ((t * 100 + i * 50) % 200)
            alpha = int(100 * (1 - radius / 200))
            if alpha > 0:
                draw.ellipse(
                    (width//2 - radius, height//2 - radius, 
                     width//2 + radius, height//2 + radius),
                    outline=(*ColorPalette.get_color(palette_name, t, 0.5), alpha),
                    width=2
                )

# ============================================================================
# 🎬 ГЛАВНЫЙ КЛАСС АНИМАЦИИ
# ============================================================================

class MaximumDancer:
    def __init__(self, width=300, height=400, fps=30, duration=10):
        self.width = width
        self.height = height
        self.fps = fps
        self.total_frames = fps * duration
        self.bg_color = (8, 10, 15)
        self.particle_count = 30
        self.glow_intensity = 4
        self.trail_length = 5
        self.prev_segments = []
        self.particles = []
        
    def simulate_beat(self, frame_idx):
        strong_beat = frame_idx % 15 == 0
        weak_beat = frame_idx % 7 == 0 and not strong_beat
        return strong_beat, weak_beat
    
    def get_current_pose(self, frame_idx):
        cycle_length = self.total_frames // 5
        cycle_t = (frame_idx % cycle_length) / cycle_length
        seq_idx = frame_idx // cycle_length % 5
        
        poses = [Choreography.idle, Choreography.wave, Choreography.jump, 
                 Choreography.spin, Choreography.hip_hop]
        
        if cycle_t < 0.9:
            return poses[seq_idx](cycle_t)
        else:
            next_pose = poses[(seq_idx + 1) % len(poses)]
            t_blend = (cycle_t - 0.9) / 0.1
            current = poses[seq_idx](0.95)
            next_p = next_pose(0.05)
            return {k: lerp(current.get(k, 0), next_p.get(k, 0), t_blend) 
                    for k in set(current) | set(next_p)}
    
    def update_particles(self, skeleton, strong_beat, color):
        for p in self.particles[:]:
            p.update()
            if not p.is_alive():
                self.particles.remove(p)
        
        if strong_beat and len(self.particles) < self.particle_count:
            segments, head, pelvis = skeleton.get_segments()
            for seg in segments[1:]:
                if random.random() < 0.3:
                    x = lerp(seg[0], seg[2], random.random())
                    y = lerp(seg[1], seg[3], random.random())
                    angle = random.uniform(0, 2*math.pi)
                    speed = random.uniform(1, 4)
                    self.particles.append(Particle(
                        x, y, color, 
                        life=random.randint(20, 40),
                        size=random.randint(2, 5),
                        vx=math.cos(angle) * speed,
                        vy=math.sin(angle) * speed - 1
                    ))
    
    def render_frame(self, frame_idx):
        strong_beat, weak_beat = self.simulate_beat(frame_idx)
        t = frame_idx / self.total_frames
        
        brightness = 1.0 + (0.3 if strong_beat else 0.1 if weak_beat else 0)
        color = ColorPalette.get_color('cyberpunk', t, brightness)
        
        img = Image.new('RGBA', (self.width, self.height), (*self.bg_color, 255))
        draw = ImageDraw.Draw(img, 'RGBA')
        
        VisualEffects.draw_background(draw, self.width, self.height, t)
        
        skeleton = Skeleton(self.width // 2, self.height // 2 + 20, scale=0.9)
        pose_data = self.get_current_pose(frame_idx)
        
        if strong_beat:
            pose_data['spine'] = pose_data.get('spine', -math.pi/2) + 0.05
        skeleton.set_pose(pose_data, t=1.0)
        
        segments, head_center, pelvis = skeleton.get_segments()
        
        if frame_idx > 0 and len(self.prev_segments) > 0:
            for i, alpha in enumerate([20, 40, 60]):
                if frame_idx > i and i < len(self.prev_segments):
                    VisualEffects.draw_motion_trail(
                        draw, self.prev_segments[-(i+1)], color, alpha
                    )
        
        VisualEffects.draw_neon_glow(draw, segments, color, self.glow_intensity)
        
        for x1, y1, x2, y2 in segments:
            draw.line((x1, y1, x2, y2), fill=color, width=3)
        
        draw.ellipse((head_center[0]-12, head_center[1]-12, 
                      head_center[0]+12, head_center[1]+12), 
                     outline=color, width=3, fill=(*color, 30))
        eye_offset = 4
        draw.point((head_center[0]-eye_offset, head_center[1]-3), fill=(255,255,255))
        draw.point((head_center[0]+eye_offset, head_center[1]-3), fill=(255,255,255))
        
        self.update_particles(skeleton, strong_beat, color)
        VisualEffects.draw_sparkles(draw, self.particles)
        
        if strong_beat:
            img = VisualEffects.apply_screen_shake(img, intensity=2, frame_idx=frame_idx)
        
        self.prev_segments.append(segments)
        if len(self.prev_segments) > self.trail_length:
            self.prev_segments.pop(0)
        
        return img.convert('RGB')
    
    def generate(self, output_path="assets/maximum_dancer.gif"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        frames = []
        
        print(f"🎬 Рендеринг {self.total_frames} кадров...")
        for i in range(self.total_frames):
            if i % 10 == 0:
                print(f"   Кадр {i}/{self.total_frames}")
            frame = self.render_frame(i)
            frames.append(frame)
        
        print("💾 Сохранение GIF...")
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=1000 // self.fps,
            disposal=2,
            optimize=True
        )
        print(f"✅ Готово: {output_path}")
        return output_path

# ============================================================================
# 🚀 ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    dancer = MaximumDancer(
        width=300,
        height=400,
        fps=24,
        duration=10
    )
    dancer.generate("assets/maximum_dancer.gif")
    
    print("🎨 Создание спрайтшита...")
    sprite_width = 300 * 10
    sprite_height = 400 * 3
    sprite = Image.new('RGB', (sprite_width, sprite_height), (8, 10, 15))
    
    frame_idx = 0
    for row in range(3):
        for col in range(10):
            if frame_idx < dancer.total_frames:
                frame = dancer.render_frame(frame_idx)
                sprite.paste(frame, (col * 300, row * 400))
                frame_idx += 1
    
    sprite.save("assets/maximum_dancer_spritesheet.png")
    print("✅ Спрайтшит: assets/maximum_dancer_spritesheet.png")
