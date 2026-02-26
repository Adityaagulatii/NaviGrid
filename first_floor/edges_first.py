import json
from PIL import Image, ImageDraw

# ── Config ─────────────────────────────────────────────────────────────────
IMAGE_PATH  = r"C:\Users\adity\Downloads\navigrid\navigrid\first_level.jpg"
NODES_JSON  = "floor1_nodes.json"
OUTPUT_IMG  = "floor1_edges_output.png"
OUTPUT_JSON = "floor1_nodemap.json"

# ── Define edges from stairs (entry point of floor 1) ─────────────────────
EDGES = [
    ["stairs", "125"],
    ["stairs", "130"],
    ["stairs", "135"],
    ["stairs", "140"],
    ["stairs", "main_hall"],
    ["stairs", "elevator"],
    ["stairs", "exit"],
]

# ── Load nodes ─────────────────────────────────────────────────────────────
with open(NODES_JSON, "r") as f:
    data = json.load(f)

nodes    = data["nodes"]
node_map = {n["id"]: n for n in nodes}
print(f"✅ Loaded {len(nodes)} nodes")

# ── Build edges ────────────────────────────────────────────────────────────
built_edges = []
for edge in EDGES:
    n1 = node_map.get(edge[0])
    n2 = node_map.get(edge[1])
    if n1 and n2:
        dx   = n1["x"] - n2["x"]
        dy   = n1["y"] - n2["y"]
        dist = round((dx**2 + dy**2) ** 0.5, 1)
        built_edges.append({"from": edge[0], "to": edge[1], "dist": dist})
        print(f"  ✅ {edge[0]} ──► {edge[1]} ({dist}px)")
    else:
        print(f"  ⚠️  Could not find: {edge[0]} or {edge[1]}")

# ── Visualize ──────────────────────────────────────────────────────────────
img  = Image.open(IMAGE_PATH).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# Draw edges
for edge in built_edges:
    n1 = node_map[edge["from"]]
    n2 = node_map[edge["to"]]
    draw.line([(n1["x"], n1["y"]), (n2["x"], n2["y"])],
              fill=(46, 204, 113, 220), width=3)

# Draw nodes
for node in nodes:
    cx, cy          = node["x"], node["y"]
    x1, y1, x2, y2 = node["x1"], node["y1"], node["x2"], node["y2"]
    draw.rectangle([x1, y1, x2, y2],
                   fill=(52, 152, 219, 60),
                   outline=(52, 152, 219, 255), width=3)
    draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=(231, 76, 60, 255))
    draw.rectangle([x1, y1-22, x1+len(node["id"])*8, y1],
                   fill=(52, 152, 219, 200))
    draw.text((x1+4, y1-20), node["id"], fill="white")

img.save(OUTPUT_IMG)
img.show()
print(f"✅ Saved {OUTPUT_IMG}")

# ── Save final nodemap ─────────────────────────────────────────────────────
with open(OUTPUT_JSON, "w") as f:
    json.dump({"nodes": nodes, "edges": built_edges}, f, indent=4)
print(f"✅ Saved {OUTPUT_JSON}")

print(f"\n📋 SUMMARY:")
print(f"  Nodes: {len(nodes)}")
print(f"  Edges: {len(built_edges)}")