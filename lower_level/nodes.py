
import csv
import json
from PIL import Image

# ── Config ─────────────────────────────────────────────────────────────────
IMAGE_PATH = r"C:\Users\adity\Downloads\navigrid\navigrid\lower_level.jpg"
CSV_PATH   = r"C:\Users\adity\Downloads\navigrid\navigrid\lower_level_annotations.csv"

# ── Load annotations and convert to nodes ─────────────────────────────────
def load_nodes(csv_path, image_path):
    nodes = []
    img   = Image.open(image_path)
    aw, ah = img.size

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Scale coordinates to actual image size
            sx = aw / int(row["image_width"])
            sy = ah / int(row["image_height"])

            x  = int(int(row["bbox_x"])      * sx)
            y  = int(int(row["bbox_y"])      * sy)
            w  = int(int(row["bbox_width"])  * sx)
            h  = int(int(row["bbox_height"]) * sy)

            # Center of the bounding box = node position
            cx = x + w // 2
            cy = y + h // 2

            node = {
                "id":   row["label_name"],  # ID comes from annotation label
                "x":    cx,
                "y":    cy,
                "x1":   x,
                "y1":   y,
                "x2":   x + w,
                "y2":   y + h,
            }
            nodes.append(node)
            print(f"  ✅ Node: {node['id']} → ({cx}, {cy})")

    return nodes

# ── Main ───────────────────────────────────────────────────────────────────
print("📐 Loading nodes from annotations...")
nodes = load_nodes(CSV_PATH, IMAGE_PATH)

print(f"\n✅ Total nodes: {len(nodes)}")

# Save to JSON
with open("nodes.json", "w") as f:
    json.dump({"nodes": nodes}, f, indent=4)

print("✅ Saved to nodes.json")

from PIL import ImageDraw

# ── Show nodes on image ────────────────────────────────────────────────────
def visualize(image_path, nodes):
    img  = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    for node in nodes:
        cx, cy = node["x"], node["y"]
        x1, y1, x2, y2 = node["x1"], node["y1"], node["x2"], node["y2"]

        # Draw box
        draw.rectangle([x1, y1, x2, y2], fill=(52, 152, 219, 60), outline=(52, 152, 219, 255), width=3)
        # Draw center dot
        draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=(231, 76, 60, 255))
        # Draw label
        draw.rectangle([x1, y1-22, x1+len(node["id"])*8, y1], fill=(52, 152, 219, 200))
        draw.text((x1+4, y1-20), node["id"], fill="white")

    img.save("nodes_output.jpeg")
    img.show()
    print("✅ Saved nodes_output.jpeg")

visualize(IMAGE_PATH, nodes)
