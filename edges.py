import json
from PIL import Image, ImageDraw

# ── Load nodes from nodes.json ─────────────────────────────────────────────
with open("nodes.json", "r") as f:
    data = json.load(f)

nodes    = data["nodes"]
node_map = {n["id"]: n for n in nodes}

# ── Define edges from entrance to every node ───────────────────────────────
EDGES = [
    ["entrance", "room_045"],
    ["entrance", "room_040"],
    ["entrance", "elevator"],
    ["entrance", "stairs"],
    ["entrance", "room_025"],
    ["entrance", "room_010"]
]

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

# ── Visualize ──────────────────────────────────────────────────────────────
img  = Image.open("nodes_output.png").convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

for edge in built_edges:
    n1 = node_map[edge["from"]]
    n2 = node_map[edge["to"]]
    draw.line([(n1["x"], n1["y"]), (n2["x"], n2["y"])],
              fill=(46, 204, 113, 220), width=3)

img.save("edges_output.png")
img.show()
print("✅ Saved edges_output.png")

# ── Save final map ─────────────────────────────────────────────────────────
with open("nodemap.json", "w") as f:
    json.dump({"nodes": nodes, "edges": built_edges}, f, indent=4)
print("✅ Saved nodemap.json")