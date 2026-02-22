import cv2
import easyocr
import json
import ollama
import numpy as np

# ── Config ─────────────────────────────────────────────────────────────────
NODEMAP_PATH      = "floor1_nodemap.json"
SIGN_MAP_PATH     = "floor1_sign_map.json"
LLAMA_MEMORY_PATH = "llama_memory.json"
CAMERA_INDEX      = 0

# ── Full route (always starts from stairs) ─────────────────────────────────
FULL_ROUTE = [
    "stairs",
    "125",
    "130",
    "135",
    "140",
    "main_hall",
    "exit"
]

# ── Load nodemap ───────────────────────────────────────────────────────────
with open(NODEMAP_PATH, "r") as f:
    data  = json.load(f)
nodes = {n["id"]: n for n in data["nodes"]}
print(f"✅ Loaded {len(nodes)} nodes")

# ── Sign map ───────────────────────────────────────────────────────────────
def load_sign_map():
    try:
        with open(SIGN_MAP_PATH, "r") as f:
            return json.load(f)
    except:
        default = {
            "125":       "125",
            "130":       "130",
            "135":       "135",
            "140":       "140",
            "main hall": "main_hall",
            "main_hall": "main_hall",
            "exit":      "exit",
            "stairs":    "stairs",
            "stair":     "stairs",
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
print(f"✅ Sign map loaded ({len(SIGN_MAP)} entries)")

# ── LLaMA memory ───────────────────────────────────────────────────────────
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

# ── LLaMA instruction ──────────────────────────────────────────────────────
def get_llama_instruction(current, next_node, route_progress):
    past = ""
    if memory["history"]:
        recent = memory["history"][-5:]
        past   = "Previous instructions:\n"
        past  += "\n".join([f"- {h['current']} → {h['next']}: {h['instruction']}"
                            for h in recent])

    prompt = f"""You are an indoor navigation assistant for Floor 1 of a university building.
Current location: {current}
Next destination: {next_node}
Progress: {route_progress}
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
            "current":     current,
            "next":        next_node,
            "instruction": instruction,
            "progress":    route_progress
        })
        if len(memory["history"]) > 20:
            memory["history"] = memory["history"][-20:]
        save_memory(memory)
        return instruction
    except:
        return f"You are at {current}. Continue to {next_node}."

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

# ── Destination selector ───────────────────────────────────────────────────
def select_destination():
    destinations = [n for n in FULL_ROUTE if n != "stairs"]
    print("\n🗺️  NaviGrid - Floor 1 Navigation")
    print("=" * 40)
    print("📍 Starting from: Stairs (default)")
    print("\n🎯 Select your destination:")
    for i, node in enumerate(destinations):
        label = node.replace("_", " ").title()
        print(f"  {i+1}. {label}")
    while True:
        try:
            choice = int(input("\nEnter number: ")) - 1
            if 0 <= choice < len(destinations):
                dest = destinations[choice]
                print(f"\n✅ Destination: {dest}")
                return dest
            else:
                print("❌ Invalid choice, try again")
        except:
            print("❌ Invalid input, try again")

# ── Navigator ──────────────────────────────────────────────────────────────
class Navigator:
    def __init__(self, route):
        self.route            = route
        self.current_step     = 0
        self.current_position = route[0]
        self.completed        = False
        self.last_instruction = f"🚶 You are on Floor 1. Walk towards {route[1]}."
        print(f"\n🗺️  Floor 1 Navigation Started!")
        print(f"📍 Starting at: {self.current_position}")
        print(f"🎯 Destination: {route[-1]}")
        print(f"➡️  {self.last_instruction}\n")

    def update(self, detected_node):
        if self.completed:
            return
        if self.current_step + 1 < len(self.route):
            next_node = self.route[self.current_step + 1]
            print(f"🔍 Detected: {detected_node} | Expected: {next_node}")
            if detected_node == next_node:
                self.current_step    += 1
                self.current_position = detected_node
                if self.current_step + 1 < len(self.route):
                    upcoming    = self.route[self.current_step + 1]
                    progress    = f"{self.current_step}/{len(self.route)-1}"
                    print(f"\n{'='*50}")
                    print(f"📍 Detected: {detected_node}")
                    print("🤖 Generating instruction...")
                    instruction = get_llama_instruction(detected_node, upcoming, progress)
                    self.last_instruction = instruction
                    print(f"🧭 {instruction}")
                    print(f"{'='*50}\n")
                else:
                    self.completed        = True
                    self.last_instruction = f"🎉 You have arrived at {detected_node}!"
                    print(self.last_instruction)

    def get_status(self):
        if self.completed:
            return f"🎉 Arrived at {self.route[-1]}!", (0, 255, 0)
        next_node = self.route[self.current_step+1] if self.current_step+1 < len(self.route) else None
        return f"📍 At: {self.current_position} | ➡️  Next: {next_node}", (0, 255, 255)

# ── Minimap ────────────────────────────────────────────────────────────────
def draw_minimap(frame, navigator):
    h, w   = frame.shape[:2]
    mw, mh = 120, 320
    margin = 10
    route  = navigator.route

    minimap = np.zeros((mh, mw, 3), dtype=np.uint8)
    minimap[:] = (15, 15, 15)

    cx      = mw // 2
    start_y = 30
    end_y   = mh - 30
    spacing = (end_y - start_y) // max(len(route) - 1, 1)

    NODE_POS = {node: (cx, start_y + i * spacing)
                for i, node in enumerate(route)}

    cv2.line(minimap, (cx, start_y), (cx, end_y), (50, 50, 50), 2)

    for i in range(navigator.current_step):
        p1 = NODE_POS[route[i]]
        p2 = NODE_POS[route[i+1]]
        cv2.line(minimap, p1, p2, (0, 180, 180), 2)

    for node, pos in NODE_POS.items():
        step = route.index(node)
        if step == navigator.current_step:
            cv2.circle(minimap, pos, 12, (0, 140, 255), -1)
            cv2.circle(minimap, pos, 14, (0, 200, 255),  2)
            cv2.putText(minimap, node[:6], (pos[0]+16, pos[1]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 200, 255), 1)
        elif step < navigator.current_step:
            cv2.circle(minimap, pos, 8, (60, 60, 60), -1)
            cv2.putText(minimap, node[:6], (pos[0]+12, pos[1]+4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.28, (80, 80, 80), 1)
        elif step == navigator.current_step + 1:
            cv2.circle(minimap, pos, 10, (0, 200, 200),  2)
            cv2.circle(minimap, pos,  4, (0, 200, 200), -1)
            cv2.putText(minimap, node[:6], (pos[0]+13, pos[1]+4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.28, (0, 200, 200), 1)
        else:
            cv2.circle(minimap, pos,  8, (20, 20, 20),    -1)
            cv2.circle(minimap, pos,  8, (140, 140, 140),  1)
            cv2.putText(minimap, node[:6], (pos[0]+11, pos[1]+4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.28, (120, 120, 120), 1)

    cv2.rectangle(minimap, (0, 0), (mw-1, mh-1), (60, 60, 60), 1)
    cv2.putText(minimap, "FLOOR 1", (cx-20, mh-8),
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
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

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
    destination = select_destination()
    dest_idx    = FULL_ROUTE.index(destination)
    route       = FULL_ROUTE[:dest_idx + 1]
    print(f"\n📍 Route: {' → '.join(route)}")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ Cannot open camera!")
        return

    print("✅ Camera opened!")
    nav          = Navigator(route)
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
        cv2.imshow("NaviGrid - Floor 1", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        if nav.completed:
            cv2.waitKey(3000)
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()