import csv
import json
from PIL import Image, ImageDraw

# ── Config ─────────────────────────────────────────────────────────────────
IMAGE_PATH  = r"C:\Users\adity\Downloads\navigrid\navigrid\first_level.jpg"
CSV_PATH    = r"C:\Users\adity\Downloads\navigrid\navigrid\first_floor_annotations.csv"
OUTPUT_IMG  = "floor1_nodes_output.png"
OUTPUT_JSON = "floor1_nodes.json"

# ── Load annotations and convert to nodes ─────────────────────────────────
def load_nodes(csv_path, image_path):
    nodes = []
    img   = Image.open(image_path)
    aw, ah = img.size

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sx = aw / int(row["image_width"])
            sy = ah / int(row["image_height"])

            x  = int(int(row["bbox_x"])      * sx)
            y  = int(int(row["bbox_y"])      * sy)
            w  = int(int(row["bbox_width"])  * sx)
            h  = int(int(row["bbox_height"]) * sy)
            cx = x + w // 2
            cy = y + h // 2

            node = {
                "id":   row["label_name"],
                "x":    cx,
                "y":    cy,
                "x1":   x,
                "y1":   y,
                "x2":   x + w,
                "y2":   y + h,
                "floor": "floor1"
            }
            nodes.append(node)
            print(f"  ✅ Node: {node['id']} → ({cx}, {cy})")

    return nodes

# ── Visualize nodes on image ───────────────────────────────────────────────
def visualize(image_path, nodes, output_path):
    img  = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    for node in nodes:
        cx, cy          = node["x"], node["y"]
        x1, y1, x2, y2 = node["x1"], node["y1"], node["x2"], node["y2"]

        # Draw box
        draw.rectangle([x1, y1, x2, y2],
                       fill=(52, 152, 219, 60),
                       outline=(52, 152, 219, 255), width=3)
        # Draw center dot
        draw.ellipse([cx-10, cy-10, cx+10, cy+10],
                     fill=(231, 76, 60, 255))
        # Draw label
        draw.rectangle([x1, y1-22, x1+len(node["id"])*8, y1],
                       fill=(52, 152, 219, 200))
        draw.text((x1+4, y1-20), node["id"], fill="white")

    img.save(output_path)
    img.show()
    print(f"✅ Saved {output_path}")

# ── Main ───────────────────────────────────────────────────────────────────
print("📐 Loading Floor 1 nodes...")
nodes = load_nodes(CSV_PATH, IMAGE_PATH)

print(f"\n✅ Total nodes: {len(nodes)}")
for n in nodes:
    print(f"  {n['id']} → ({n['x']}, {n['y']})")

# Save to JSON
with open(OUTPUT_JSON, "w") as f:
    json.dump({"nodes": nodes, "edges": []}, f, indent=4)
print(f"✅ Saved {OUTPUT_JSON}")

# Visualize
visualize(IMAGE_PATH, nodes, OUTPUT_IMG)