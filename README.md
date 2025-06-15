# Relaxing Desktop Animation Generator

This Python script allows you to create relaxing animated desktop videos by applying customizable visual effects to static 1920x1080 images.

🎨 **Fully customizable**  
🌀 **Loop-ready**  
🎥 **Silent video output**  
📸 **Optional frame export**

---

## ✨ Available Effects

You can combine multiple effects:
- `ZOOM`: slow in/out movement
- `SPARKLE PARTICLES`: soft sparkles floating over the image
- `FOG`: horizontal fog drift
- `PULSATION`: brightness breathing
- `HUE SHIFT`: hue cycling for ambient color change
- `MOVING REFLECTION`: diagonal reflective sweep
- `RAIN`: animated rain effect
- `WAVE DISTORTION`: dreamy wave distortion
- `GLOW`: soft ambient glow effect that pulses over time

---

## 📁 Folder Structure

```
.
├── input/              # Drop your background images here
├── output/             # Animated videos will be saved here
├── frames/             # Optional: single frames for each animation
├── desktop_animation.py
├── requirements.txt
└── README.md
```

---

## ✅ Installation

Make sure you have Python 3.10+ installed.

Install the dependencies:

```
pip install -r requirements.txt
```

---

## ▶️ How to Use

1. Place one or more `.png`, `.jpg`, or `.jpeg` files in the `input/` folder
2. Run the script:

```
python desktop_animation.py
```

3. Follow the interactive menu to:
   - Select the background image
   - Choose the animation effects
   - Optionally enable looping and frame saving

---

## 🎬 Output

- A silent `.mp4` video will be created in the `output/` folder.
- If selected, frames will be exported to `frames/<video_name>/`.

All videos are HD (1920x1080) and optimized for use as desktop wallpapers or background loops.

---

## 📄 License

MIT License
