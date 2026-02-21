
import ollama
import json
from PIL import Image, ImageDraw

IMAGE_PATH = r"C:\Users\adity\Downloads\navigrid\navigrid\IMG_6073.jpg"  # ← change to your image path

# ── Step 1: Ask LLaVA to detect rooms ─────────────────────────────────────
print("🔍 Analyzing floorplan...")

prompt = (
    "Look at this floorplan image. "
    "Detect all rooms and estimate their position as a percentage of the image size. "
    "Return ONLY this JSON, nothing else: "
    '{"rooms": [{"name": "Room Name", "type": "room type", "x": 10, "y": 80, "w": 20, "h": 15}]} '
    "x,y = top-left corner as % of image width/height. "
    "w,h = width and height as % of image width/height."
)

response = ollama.chat(
    model="llava",
    messages=[{
        "role": "user",
        "content": prompt,
        "images": [IMAGE_PATH]
    }]
)
 #── Step 2: Parse response ─────────────────────────────────────────────────
raw = response["message"]["content"].strip()
print("Raw response:", raw)

if "```" in raw:
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    raw = raw.split("```")[0]

try:
    data = json.loads(raw.strip())
    print(f"✅ Found {len(data['rooms'])} rooms!")
except:
    print("⚠️ Could not parse, using sample data")
    data = {
        "rooms": [
            {"name": "Entrance",  "type": "entrance",  "x": 45, "y": 85, "w": 10, "h": 10},
            {"name": "Corridor",  "type": "corridor",  "x": 20, "y": 45, "w": 60, "h": 10},
            {"name": "Restroom",  "type": "restroom",  "x": 10, "y": 10, "w": 15, "h": 20},
            {"name": "Office 1",  "type": "office",    "x": 30, "y": 10, "w": 20, "h": 30},
            {"name": "Office 2",  "type": "office",    "x": 55, "y": 10, "w": 20, "h": 30},
        ]
    }

# ── Step 3: Draw boxes on image ────────────────────────────────────────────
COLORS = {
    "entrance": "#2ecc71",
    "corridor": "#3498db",
    "restroom": "#e74c3c",
    "office":   "#f39c12",
    "stairs":   "#9b59b6",
    "elevator": "#1abc9c",
}

img  = Image.open(IMAGE_PATH).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")
W, H = img.size

for room in data["rooms"]:
    x = int(room["x"] / 100 * W)
    y = int(room["y"] / 100 * H)
    w = int(room["w"] / 100 * W)
    h = int(room["h"] / 100 * H)

    color = COLORS.get(room["type"].lower(), "#95a5a6")
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    # Draw filled box
    draw.rectangle([x, y, x+w, y+h], fill=(r, g, b, 80), outline=(r, g, b, 255), width=3)

    # Draw label
    draw.rectangle([x, y-20, x+w, y], fill=(r, g, b, 200))
    draw.text((x+5, y-18), room["name"], fill="white")

# ── Step 4: Save and show ──────────────────────────────────────────────────
img.save("detected.png")
print("✅ Saved as detected.png")
img.show()