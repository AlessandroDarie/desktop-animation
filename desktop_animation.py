import os
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from math import cos, sin, pi
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from scipy.ndimage import map_coordinates
import sys

# === CONFIG ===
input_folder = "input"
output_folder = "output"
frames_folder = "frames"
fps = 24
duration = 10
frame_count = duration * fps

# === EASING ===
def ease_sine(t):
    return (1 - cos(pi * t)) / 2

# === SPARKLE PARTICLES ===
def generate_static_particles(n=20, radius_range=(1, 3), base_alpha=30, max_alpha=70):
    return [{
        'x': random.randint(0, 1920),
        'y': random.randint(0, 1080),
        'r': random.randint(*radius_range),
        'phase': random.uniform(0, 2 * pi),
        'base_alpha': base_alpha,
        'max_alpha': max_alpha
    } for _ in range(n)]

def overlay_particles(image: Image.Image, particles, t_norm):
    img = image.convert("RGBA")
    draw = ImageDraw.Draw(img)
    for p in particles:
        alpha = p['base_alpha'] + int((p['max_alpha'] - p['base_alpha']) * 0.5 * (1 + cos(2 * pi * t_norm + p['phase'])))
        color = (255, 255, 255, alpha)
        dx = int(1.5 * cos(2 * pi * t_norm + p['phase']))
        dy = int(1.5 * sin(2 * pi * t_norm + p['phase']))
        x = p['x'] + dx
        y = p['y'] + dy
        r = p['r']
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)
    return img.convert("RGB")

# === FOG ===
def overlay_fog(image: Image.Image, t_norm):
    fog = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(fog)
    for i in range(0, 1920, 120):
        x = int((i + t_norm * 300) % 1920)
        draw.rectangle([x, 0, x + 40, 1080], fill=(200, 200, 200, 12))
    return Image.alpha_composite(image.convert("RGBA"), fog).convert("RGB")

# === MOVING REFLECTION ===
def overlay_reflection(image: Image.Image, t_norm):
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    x_start = int((t_norm * (width + height)) % (width + height)) - height
    for offset in range(-200, 200, 4):
        alpha = int(80 * (1 - abs(offset) / 200))
        draw.line(
            [(x_start + offset, 0), (x_start + offset + height, height)],
            fill=(255, 255, 255, alpha),
            width=2
        )
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

# === RAIN ===
def overlay_rain(image: Image.Image, t_norm):
    rain = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(rain)
    for _ in range(120):
        x = random.randint(0, image.size[0])
        y = int((random.randint(0, image.size[1]) + t_norm * 200) % image.size[1])
        draw.line([(x, y), (x + 2, y + 10)], fill=(180, 180, 255, 100), width=1)
    return Image.alpha_composite(image.convert("RGBA"), rain).convert("RGB")

# === ZOOM ===
def apply_zoom(image: Image.Image, t_norm):
    w, h = image.size
    scale = 1.0 + 0.05 * ease_sine(t_norm)
    new_w = int(w / scale)
    new_h = int(h / scale)
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    cropped = image.crop((left, top, left + new_w, top + new_h))
    return cropped.resize((1920, 1080), Image.LANCZOS)

# === PULSATION ===
def apply_pulsation(image: Image.Image, t_norm):
    factor = 0.9 + 0.2 * ease_sine(t_norm)
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

# === HUE SHIFT ===
def apply_hue_shift(image: Image.Image, t_norm):
    img = image.convert("RGB")
    arr = np.array(img).astype(np.uint8)
    hsv = np.array(Image.fromarray(arr).convert("HSV"))
    shift = int(255 * ease_sine(t_norm))
    hsv[..., 0] = (hsv[..., 0] + shift) % 255
    return Image.fromarray(hsv, mode="HSV").convert("RGB")

# === WAVE DISTORTION ===
def apply_wave(image: Image.Image, t_norm):
    arr = np.array(image)
    rows, cols = arr.shape[:2]
    x_wave = np.arange(cols)[None, :] + 10 * np.sin(2 * pi * np.arange(rows)[:, None] / 50 + t_norm * 2 * pi)
    coords = np.array([np.repeat(np.arange(rows)[:, None], cols, axis=1), x_wave])
    warped = np.zeros_like(arr)
    for i in range(3):
        warped[..., i] = map_coordinates(arr[..., i], coords, order=1, mode='reflect')
    return Image.fromarray(warped)

# === GLOW EFFECT ===
def apply_glow(image: Image.Image, t_norm):
    glow_intensity = 0.3 + 0.7 * ease_sine(t_norm)  # oscillates between 0.3 and 1.0
    blurred = image.filter(ImageFilter.GaussianBlur(radius=15))
    return Image.blend(image, blurred, alpha=glow_intensity)

# === FRAME GENERATION ===
def generate_frames(image_path, effects, mirror_loop):
    base_img = Image.open(image_path).convert("RGB").resize((1920, 1080))
    particles = generate_static_particles(n=20) if "SPARKLE PARTICLES" in effects else []
    frames = []

    total = frame_count
    if mirror_loop:
        total *= 2

    print("\n📸 Generating frames:")
    for i in range(frame_count):
        t_norm = i / frame_count
        frame = base_img.copy()

        if "SPARKLE PARTICLES" in effects:
            frame = overlay_particles(frame, particles, t_norm)
        if "FOG" in effects:
            frame = overlay_fog(frame, t_norm)
        if "MOVING REFLECTION" in effects:
            frame = overlay_reflection(frame, t_norm)
        if "RAIN" in effects:
            frame = overlay_rain(frame, t_norm)
        if "ZOOM" in effects:
            frame = apply_zoom(frame, t_norm)
        if "PULSATION" in effects:
            frame = apply_pulsation(frame, t_norm)
        if "HUE SHIFT" in effects:
            frame = apply_hue_shift(frame, t_norm)
        if "WAVE DISTORTION" in effects:
            frame = apply_wave(frame, t_norm)
        if "GLOW" in effects:
            frame = apply_glow(frame, t_norm)    

        frames.append(np.array(frame))

        print(f"\rProgress: {i + 1}/{frame_count} frame(s)", end="")
        sys.stdout.flush()

    print("\n✅ Frames generated.")

    if mirror_loop:
        print("🔁 Adding reversed frames for loop...")
        frames += frames[::-1]
        print("✅ Total frames:", len(frames))

    return frames

# === SAVE INDIVIDUAL FRAMES ===
def save_frames_as_images(frames, name):
    path = os.path.join(frames_folder, name)
    os.makedirs(path, exist_ok=True)
    print(f"💾 Saving frames to '{path}'...")
    for i, frame in enumerate(frames):
        Image.fromarray(frame).save(os.path.join(path, f"frame_{i:04d}.png"))
        if i % 10 == 0 or i == len(frames) - 1:
            print(f"\rSaved: {i + 1}/{len(frames)}", end="")
            sys.stdout.flush()
    print("\n✅ Frames saved.")

# === CREATE VIDEO ===
def create_video(frames, name):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, name + ".mp4")
    print(f"\n🎞️ Creating final video at {output_path}...")
    clip = ImageSequenceClip(frames, fps=fps)
    clip.write_videofile(output_path, codec="libx264", audio=False)
    print("✅ Video saved.")

# === SELECT BACKGROUND FILE ===
def select_background():
    files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    if not files:
        print("❌ No image found in the 'input/' folder.")
        return None

    print("🖼️ Available backgrounds:")
    for i, f in enumerate(files):
        print(f"{i + 1}. {f}")

    while True:
        choice = input("\nSelect the background by typing its number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            return files[int(choice) - 1]
        else:
            print("❗ Invalid selection.")

# === SELECT ANIMATIONS ===
def select_animations():
    available = ["ZOOM", "SPARKLE PARTICLES", "FOG", "PULSATION", "HUE SHIFT", "MOVING REFLECTION", "RAIN", "WAVE DISTORTION","GLOW"]
    selected = []

    print("\n✨ Available animations:")
    for i, name in enumerate(available):
        print(f"{i + 1}. {name}")

    while True:
        choice = input("\nSelect an animation by typing its number, or press Enter to continue: ").strip()
        if choice == "":
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(available):
            effect = available[int(choice) - 1]
            if effect not in selected:
                selected.append(effect)
                print(f"✔ Added: {effect}")
            else:
                print("(already selected)")
        else:
            print("❗ Invalid selection.")

    if not selected:
        print("⚠ No animation selected. Exiting.")
        return None

    return selected

# === LOOP MIRROR OPTION ===
def ask_loop_mirror():
    choice = input("\nDo you want to enable perfect loop (append reversed frames)? [y/N]: ").strip().lower()
    return choice == "y"

# === SAVE INDIVIDUAL FRAMES OPTION ===
def ask_save_frames():
    choice = input("\nDo you want to also save individual animation frames? [y/N]: ").strip().lower()
    return choice == "y"

# === MAIN ===
def main():
    print("=== Relaxing Desktop Animation Generator ===\n")
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(frames_folder, exist_ok=True)

    bg_file = select_background()
    if not bg_file:
        return

    effects = select_animations()
    if not effects:
        return

    mirror_loop = ask_loop_mirror()
    save_frames = ask_save_frames()

    input_path = os.path.join(input_folder, bg_file)
    base_name = os.path.splitext(bg_file)[0]
    output_name = base_name + "_" + "_".join(effects)
    if mirror_loop:
        output_name += "_loop"

    frames = generate_frames(input_path, effects, mirror_loop)
    if save_frames:
        save_frames_as_images(frames, output_name)
    create_video(frames, output_name)

if __name__ == "__main__":
    main()

