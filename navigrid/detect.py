import ollama
import json
from PIL import Image, ImageDraw
from ultralytics import YOLO

IMAGE_PATH = r"C:\Users\adity\Downloads\navigrid\navigrid\izrvqavii6db1.jpg"  # ← change to your image path
USER_QUERY = "How do I get from the entrance to the restroom?"  # ← change query

# ── Step 1: YOLO detects regions ───────────────────────────────────────────
print("🔍 Step 1: YOLO detecting regions...")

model   = YOLO("yolov8n.pt")
results = model(IMAGE_PATH)
img     = Image.open(IMAGE_PATH).convert("RGB")
W, H    = img.size

boxes = []
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        if float(box.conf[0]) > 0.3:
            boxes.append((x1, y1, x2, y2))

# fallback grid if YOLO finds nothing
if len(boxes) == 0:
    print("⚠️  YOLO found nothing, using grid...")
    gw, gh = W // 4, H // 4
    for row in range(4):
        for col in range(4):
            boxes.append((col*gw, row*gh, (col+1)*gw, (row+1)*gh))

print(f"✅ Found {len(boxes)} regions")

# ── Step 2: Convert to nodes ───────────────────────────────────────────────
nodes = []
for i, (x1, y1, x2, y2) in enumerate(boxes):
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    nodes.append({
        "id":     f"N{i+1}",
        "center": (cx, cy),
        "x1": x1, "y1": y1,
        "x2": x2, "y2": y2
    })

# ── Step 3: Connect nearby nodes ──────────────────────────────────────────
edges = []
for i, n1 in enumerate(nodes):
    for j, n2 in enumerate(nodes):
        if i >= j:
            continue
        dx = abs(n1["center"][0] - n2["center"][0])
        dy = abs(n1["center"][1] - n2["center"][1])
        dist = (dx**2 + dy**2) ** 0.5
        if dist < W * 0.3:
            edges.append({
                "from": n1["id"],
                "to":   n2["id"],
                "dist": round(dist)
            })

print(f"✅ Built {len(edges)} connections")

# ── Step 4: Draw nodes on image ────────────────────────────────────────────
draw = ImageDraw.Draw(img, "RGBA")

# Draw edges
for e in edges:
    n1 = next(n for n in nodes if n["id"] == e["from"])
    n2 = next(n for n in nodes if n["id"] == e["to"])
    draw.line([n1["center"], n2["center"]], fill=(100, 100, 255, 180), width=2)

# Draw nodes
for node in nodes:
    cx, cy = node["center"]
    draw.rectangle([node["x1"], node["y1"], node["x2"], node["y2"]],
                   fill=(52, 152, 219, 60), outline=(52, 152, 219, 255), width=2)
    draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=(231, 76, 60, 255))
    draw.text((cx-10, cy-8), node["id"], fill="white")

img.save("nodes_output.png")
print("✅ Node map saved as nodes_output.png")
img.show()

# ── Step 5: LLaVA generates navigation from nodes ─────────────────────────
print(f"\n🧠 Step 5: Generating navigation for: '{USER_QUERY}'")

node_map = {
    "nodes": [{"id": n["id"], "center": n["center"]} for n in nodes],
    "edges": edges
}

prompt = (
    f"You are an indoor navigation assistant for blind and low vision users. "
    f"Here is a node map of a building extracted from a floorplan: "
    f"{json.dumps(node_map)} "
    f"Each node is a region in the building connected to nearby nodes. "
    f"User query: '{USER_QUERY}' "
    f"Give clear step by step navigation instructions using the node IDs. "
    f"Mention turns, distances and node references. "
    f"Be concise and voice friendly."
)

response = ollama.chat(
    model="llava",
    messages=[{
        "role": "user",
        "content": prompt,
        "images": [IMAGE_PATH]
    }]
)

instructions = response["message"]["content"].strip()

print("\n🧭 NAVIGATION INSTRUCTIONS:")
print("=" * 40)
print(instructions)