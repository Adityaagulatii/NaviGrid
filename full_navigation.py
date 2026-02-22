import cv2
import easyocr
import json
import ollama
import numpy as np

# ── Config ─────────────────────────────────────────────────────────────────
LOWER_NODEMAP     = "nodemap_final.json"
FLOOR1_NODEMAP    = "floor1_nodemap.json"
SIGN_MAP_PATH     = "sign_map.json"
LLAMA_MEMORY_PATH = "llama_memory.json"
CAMERA_INDEX      = 0

# ── Lower level route ──────────────────────────────────────────────────────
LOWER_ROUTE = [
    "entrance",
    "room_045",
    "room_040",
    "stairs",
    "room_025",
    "room_010"
]

# ── Floor 1 route (starts from stairs) ────────────────────────────────────
FLOOR1_ROUTE = [
    "stairs",
    "125",
    "130",
    "135",
    "140",
    "main_hall",
    "exit"
]

# ── All destinations with floor info ──────────────────────────────────────
ALL_DESTINATIONS = {
    # Lower level
    "room_045": {"floor": "lower", "label": "Room 045 - Active Learning"},
    "room_040": {"floor": "lower", "label": "Room 040"},
    "stairs":   {"floor": "lower", "label": "Stairs"},
    "room_025": {"floor": "lower", "label": "Room 025"},
    "room_010": {"floor": "lower", "label": "Room 010"},
    # Floor 1
    "125":      {"floor": "floor1", "label": "Floor 1 - Room 125"},
    "130":      {"floor": "floor1", "label": "Floor 1 - Room 130"},
    "135":      {"floor": "floor1", "label": "Floor 1 - Room 135"},
    "140":      {"floor": "floor1", "label": "Floor 1 - Room 140"},
    "main_hall":{"floor": "floor1", "label": "Floor 1 - Main Hall"},
    "exit":     {"floor": "floor1", "label": "Floor 1 - Exit"},
}

# ── Load nodemaps ──────────────────────────────────────────────────────────
with open(LOWER_NODEMAP, "r") as f:
    lower_data  = json.load(f)
with open(FLOOR1_NODEMAP, "r") as f:
    floor1_data = json.load(f)

lower_nodes  = {n["id"]: n for n in lower_data["nodes"]}
floor1_nodes = {n["id"]: n for n in floor1_data["nodes"]}
print(f"✅ Loaded {len(lower_nodes)} lower level nodes")
print(f"✅ Loaded {len(floor1_nodes)} floor 1 nodes")

# ── Sign map ───────────────────────────────────────────────────────────────
def load_sign_map():
    try:
        with open(SIGN_MAP_PATH, "r") as f:
            return json.load(f)
    except:
        default = {
            "045":             "room_045",
            "040":             "room_040",
            "025":             "room_025",
            "010":             "room_010",
            "active learning": "room_045",
            "stair":           "stairs",
            "stairs":          "stairs",
            "125":             "125",
            "130":             "130",
            "135":             "135",
            "140":             "140",
            "main hall":       "main_hall",
            "exit":            "exit",
        }
        with open(SIGN_MAP_PATH, "w") as f:
            json.dump(default, f, indent=4)
        return default

def save_sign_map(sign_map):
    with open(SIGN_MAP_PATH, "w") as f:
        json.dump(sign_map, f, indent=4)

def update_sign_map(text, node_id, sign_map):
    text_lower = text.lower().strip()
    if text_lower not in sign_map:
        sign_map[text_lower] = node_id
        save_sign_map(sign_map)
        print(f"✅ New sign learned: '{text_lower}' → {node_id}")
    return sign_map

SIGN_MAP = load_sign_map()

# ── LLaMA ──────────────────────────────────────────────────────────────────
def load_memory():
    try:
        with open(LLAMA_MEMORY_PATH, "r") as f:
            return json.load(f)
    except:
        return {"history": [], "feedback": {}}

def save_memory(memory):
    with open(LLAMA_MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=4)

memory = load_memory()

def get_llama_instruction(current, next_node, floor, progress):
    past = ""
    if memory["history"]:
        recent = memory["history"][-5:]
        past   = "Previous instructions:\n"
        past  += "\n".join([f"- {h['current']} → {h['next']}: {h['instruction']}"
                            for h in recent])

    # Special instruction for floor transition
    if current == "stairs" and next_node in FLOOR1_ROUTE:
        extra = "The user is transitioning from Lower Level to Floor 1 via stairs."
    else:
        extra = f"Floor: {floor}"

    prompt = f"""You are an indoor navigation assistant for a university building.
Current location: {current}
Next destination: {next_node}
{extra}
Progress: {progress}
{past}

Give a short friendly natural navigation instruction in 1-2 sentences.
No markdown, plain text only."""

    try:
        response    = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}]
        )
        instruction = response["message"]["content"].strip()
        memory["history"].append({
            "current": current, "next": next_node,
            "instruction": instruction, "progress": progress
        })
        if len(memory["history"]) > 20:
            memory["history"] = memory["history"][-20:]
        save_memory(memory)
        return instruction
    except:
        return f"Continue from {current} to {next_node}."

# ── OCR ────────────────────────────────────────────────────────────────────
print("🔤 Loading OCR...")
reader = easyocr.Reader(["en"], gpu=True)
print("✅ OCR ready")

def match_text(texts):
    for text, conf in texts:
        text_lower = text.lower().strip()
        for key, node_id in SIGN_MAP.items():
            if key in text_lower and conf > 0.4:
                update_sign_map(text_lower, node_id, SIGN_MAP)
                return node_id, text, conf
    return None, None, 0

# ── Build full route ───────────────────────────────────────────────────────
def build_route(destination):
    dest_info = ALL_DESTINATIONS[destination]

    if dest_info["floor"] == "lower":
        # Destination on lower level
        dest_idx = LOWER_ROUTE.index(destination)
        return LOWER_ROUTE[:dest_idx + 1], "lower"
    else:
        # Destination on floor 1
        # Go from entrance to stairs on lower level
        stairs_idx  = LOWER_ROUTE.index("stairs")
        lower_part  = LOWER_ROUTE[:stairs_idx + 1]
        # Then from stairs to destination on floor 1
        dest_idx    = FLOOR1_ROUTE.index(destination)
        floor1_part = FLOOR1_ROUTE[:dest_idx + 1]
        # Combine (stairs appears in both, remove duplicate)
        full_route  = lower_part + floor1_part[1:]
        return full_route, "multi"

# ── Destination selector ───────────────────────────────────────────────────
def select_destination():
    print("\n🗺️  NaviGrid - Full Building Navigation")
    print("=" * 40)
    print("📍 Starting from: Entrance (Lower Level)")
    print("\n🎯 Select your destination:")

    dest_list = list(ALL_DESTINATIONS.keys())
    for i, node in enumerate(dest_list):
        info  = ALL_DESTINATIONS[node]
        floor = "🏢 Floor 1" if info["floor"] == "floor1" else "⬇️  Lower Level"
        print(f"  {i+1}. {info['label']} [{floor}]")

    while True:
        try:
            choice = int(input("\nEnter number: ")) - 1
            if 0 <= choice < len(dest_list):
                dest = dest_list[choice]
                print(f"\n✅ Destination: {ALL_DESTINATIONS[dest]['label']}")
                return dest
            else:
                print("❌ Invalid choice")
        except:
            print("❌ Invalid input")

# ── Navigator ──────────────────────────────────────────────────────────────
class Navigator:
    def __init__(self, route, floor_type):
        self.route            = route
        self.floor_type       = floor_type
        self.current_step     = 0
        self.current_position = route[0]
        self.current_floor    = "lower"
        self.completed        = False
        self.last_instruction = f"🚶 Walk straight down the corridor to {route[1]}."
        print(f"\n🗺️  Navigation Started!")
        print(f"📍 Start: {self.current_position}")
        print(f"🎯 Destination: {route[-1]}")
        print(f"➡️  {self.last_instruction}\n")

    def update(self, detected_node):
        if self.completed:
            return
        if self.current_step + 1 < len(self.route):
            next_node = self.route[self.current_step + 1]
            if detected_node == next_node:
                self.current_step    += 1
                self.current_position = detected_node

                # Update floor
                if detected_node in FLOOR1_ROUTE:
                    self.current_floor = "floor1"

                if self.current_step + 1 < len(self.route):
                    upcoming    = self.route[self.current_step + 1]
                    progress    = f"{self.current_step}/{len(self.route)-1}"
                    print(f"\n{'='*50}")
                    print(f"📍 Detected: {detected_node}")
                    print("🤖 Generating instruction...")
                    instruction = get_llama_instruction(
                        detected_node, upcoming,
                        self.current_floor, progress
                    )
                    self.last_instruction = instruction
                    print(f"🧭 {instruction}")
                    print(f"{'='*50}\n")
                else:
                    self.completed        = True
                    self.last_instruction = f"🎉 You have arrived at {detected_node}!"
                    print(self.last_instruction)

    def get_status(self):
        floor_label = "Floor 1" if self.current_floor == "floor1" else "Lower Level"
        if self.completed:
            return f"🎉 Arrived at {self.route[-1]}!", (0, 255, 0)
        next_node = self.route[self.current_step+1] if self.current_step+1 < len(self.route) else None
        return f"[{floor_label}] 📍 {self.current_position} | ➡️  {next_node}", (0, 255, 255)

# ── Minimap ────────────────────────────────────────────────────────────────
def draw_minimap(frame, navigator):
    h, w   = frame.shape[:2]
    mw, mh = 130, 340
    margin = 10
    route  = navigator.route

    minimap = np.zeros((mh, mw, 3), dtype=np.uint8)
    minimap[:] = (15, 15, 15)

    cx      = mw // 2
    start_y = 25
    end_y   = mh - 25
    spacing = (end_y - start_y) // max(len(route) - 1, 1)

    NODE_POS = {node: (cx, start_y + i * spacing)
                for i, node in enumerate(route)}

    # Draw floor separator line at stairs
    if "stairs" in route and navigator.floor_type == "multi":
        stairs_y = NODE_POS["stairs"][1]
        cv2.line(minimap, (5, stairs_y), (mw-5, stairs_y), (100, 100, 0), 1)
        cv2.putText(minimap, "F1", (5, stairs_y - 3),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.25, (100, 100, 0), 1)

    # Draw corridor
    cv2.line(minimap, (cx, start_y), (cx, end_y), (50, 50, 50), 2)

    # Draw visited path
    for i in range(navigator.current_step):
        p1 = NODE_POS[route[i]]
        p2 = NODE_POS[route[i+1]]
        cv2.line(minimap, p1, p2, (0, 180, 180), 2)

    # Draw nodes
    for node, pos in NODE_POS.items():
        step  = route.index(node)
        label = node.replace("room_", "R")[:6]

        if step == navigator.current_step:
            cv2.circle(minimap, pos, 12, (0, 140, 255), -1)
            cv2.circle(minimap, pos, 14, (0, 200, 255),  2)
            cv2.putText(minimap, label, (pos[0]+16, pos[1]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 200, 255), 1)
        elif step < navigator.current_step:
            cv2.circle(minimap, pos, 8, (60, 60, 60), -1)
            cv2.putText(minimap, label, (pos[0]+12, pos[1]+4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.28, (80, 80, 80), 1)
        elif step == navigator.current_step + 1:
            cv2.circle(minimap, pos, 10, (0, 200, 200),  2)
            cv2.circle(minimap, pos,  4, (0, 200, 200), -1)
            cv2.putText(minimap, label, (pos[0]+13, pos[1]+4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 200, 200), 1)
        else:
            cv2.circle(minimap, pos,  8, (20, 20, 20),    -1)
            cv2.circle(minimap, pos,  8, (140, 140, 140),  1)
            cv2.putText(minimap, label, (pos[0]+11, pos[1]+4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.28, (120, 120, 120), 1)

    cv2.rectangle(minimap, (0, 0), (mw-1, mh-1), (60, 60, 60), 1)
    floor_label = "FLOOR 1" if navigator.current_floor == "floor1" else "LOWER LVL"
    cv2.putText(minimap, floor_label, (cx-25, mh-8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1)

    x1      = w - mw - margin
    y1      = margin
    roi     = frame[y1:y1+mh, x1:x1+mw]
    blended = cv2.addWeighted(roi, 0.2, minimap, 0.8, 0)
    frame[y1:y1+mh, x1:x1+mw] = blended
    return frame

# ── Draw overlay ───────────────────────────────────────────────────────────
def draw_overlay(frame, ocr_results, navigator, detected):
    h, w = frame.shape[:2]

    for (bbox, text, prob) in ocr_results:
        if prob > 0.4:
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame, f"{text}({prob:.2f})",
                        (pts[0][0], pts[0][1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    status, color = navigator.get_status()
    cv2.rectangle(frame, (0, 0), (w, 90), (0, 0, 0), -1)
    cv2.putText(frame, status, (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

    progress = navigator.current_step / max(len(navigator.route)-1, 1)
    bar_w    = int(w * progress)
    cv2.rectangle(frame, (0, 60), (w, 80),     (50, 50, 50), -1)
    cv2.rectangle(frame, (0, 60), (bar_w, 80), (0, 255, 0),  -1)

    if detected:
        cv2.putText(frame, f"Detected: {detected}",
                    (10, h-80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    words = navigator.last_instruction.split()
    line1 = ' '.join(words[:8])
    line2 = ' '.join(words[8:16])
    cv2.rectangle(frame, (0, h-60), (w, h), (0, 0, 0), -1)
    cv2.putText(frame, line1, (10, h-38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    cv2.putText(frame, line2, (10, h-15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

    return frame

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    destination       = select_destination()
    route, floor_type = build_route(destination)
    print(f"\n📍 Full Route: {' → '.join(route)}")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ Cannot open camera!")
        return

    print("✅ Camera opened!")
    nav          = Navigator(route, floor_type)
    frame_count  = 0
    ocr_results  = []
    last_matched = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        if frame_count % 5 == 0:
            results     = reader.readtext(frame)
            ocr_results = results
            texts       = [(r[1], r[2]) for r in results]
            node, text, conf = match_text(texts)
            if node:
                last_matched = node
                nav.update(node)

        frame = draw_overlay(frame, ocr_results, nav, last_matched)
        frame = draw_minimap(frame, nav)
        cv2.imshow("NaviGrid - Full Navigation", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if nav.completed:
            cv2.waitKey(3000)
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()