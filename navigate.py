import cv2
import easyocr
import json
import time

# ── Config ─────────────────────────────────────────────────────────────────
NODEMAP_PATH = "nodemap_final.json"
CAMERA_INDEX = 0

# ── Route from entrance ────────────────────────────────────────────────────
ROUTE = [
    "entrance",
    "room_045",
    "room_040",
    "stairs",
    "room_025",
    "room_010"
]

# ── Instructions for each step ─────────────────────────────────────────────
INSTRUCTIONS = {
    "entrance":  "🚶 You are at the entrance. Walk straight down the corridor.",
    "room_045":  "✅ You reached Room 045. Continue straight to Room 040.",
    "room_040":  "✅ You reached Room 040. Continue straight to the stairs.",
    "stairs":    "✅ You reached the Stairs. Continue straight to Room 025.",
    "room_025":  "✅ You reached Room 025. Continue straight to Room 010.",
    "room_010":  "🎉 You reached Room 010. You have completed the route!"
}

# ── Sign map ───────────────────────────────────────────────────────────────
SIGN_MAP = {
    "045":            "room_045",
    "040":            "room_040",
    "025":            "room_025",
    "010":            "room_010",
    "active learning": "room_045",
    "stair":          "stairs",
    "stairs":         "stairs",
}

# ── Load nodemap ───────────────────────────────────────────────────────────
with open("nodemap_final.json", "r") as f:
    data = json.load(f)
nodes = {n["id"]: n for n in data["nodes"]}
print(f"✅ Loaded {len(nodes)} nodes")

# ── Initialize OCR ─────────────────────────────────────────────────────────
print("🔤 Loading OCR...")
reader = easyocr.Reader(["en"], gpu=True)
print("✅ OCR ready")

# ── Match OCR text to node ─────────────────────────────────────────────────
def match_text(texts):
    for text, conf in texts:
        text_lower = text.lower().strip()
        for key, node_id in SIGN_MAP.items():
            if key in text_lower and conf > 0.4:
                return node_id, text, conf
    return None, None, 0

# ── Navigation state ───────────────────────────────────────────────────────
class Navigator:
    def __init__(self):
        self.current_step     = 0
        self.current_position = ROUTE[0]
        self.completed        = False
        print(f"\n🗺️  NaviGrid Navigation Started!")
        print(f"📍 Starting at: {self.current_position}")
        print(f"➡️  {INSTRUCTIONS[self.current_position]}\n")

    def update(self, detected_node):
        if self.completed:
            return

        # Check if detected node is next in route
        if self.current_step + 1 < len(ROUTE):
            next_node = ROUTE[self.current_step + 1]

            if detected_node == next_node:
                self.current_step    += 1
                self.current_position = detected_node

                instruction = INSTRUCTIONS.get(detected_node, "")
                print(f"\n{'='*50}")
                print(instruction)
                print(f"{'='*50}\n")

                if self.current_step == len(ROUTE) - 1:
                    self.completed = True
                    print("🎉 Navigation complete!")

    def get_status(self):
        if self.completed:
            return "🎉 Route Complete!", (0, 255, 0)
        next_node = ROUTE[self.current_step + 1] if self.current_step + 1 < len(ROUTE) else None
        status    = f"📍 At: {self.current_position} | ➡️  Next: {next_node}"
        return status, (0, 255, 255)

# ── Draw mini floorplan ────────────────────────────────────────────────────
def draw_minimap(frame, navigator):
    h, w  = frame.shape[:2]
    mw, mh = 200, 350  # minimap size
    margin = 10

    # Background
    minimap = frame[margin:margin+mh, w-mw-margin:w-margin].copy()
    cv2.rectangle(minimap, (0, 0), (mw, mh), (30, 30, 30), -1)
    cv2.putText(minimap, "FLOOR MAP", (50, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Node positions on minimap
    NODE_POS = {
        "entrance":  (100, 50),
        "room_045":  (100, 90),
        "room_040":  (100, 130),
        "stairs":    (100, 170),
        "room_025":  (100, 230),
        "room_010":  (100, 290),
    }

    # Draw corridor line
    cv2.line(minimap, (100, 50), (100, 310), (100, 100, 100), 2)

    # Draw each node
    for node, pos in NODE_POS.items():
        step = ROUTE.index(node)

        if node == navigator.current_position:
            # Current position = big green circle
            cv2.circle(minimap, pos, 14, (0, 255, 0), -1)
            cv2.putText(minimap, node.replace("room_", ""),
                        (pos[0]+16, pos[1]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        elif step < navigator.current_step:
            # Already visited = small grey circle
            cv2.circle(minimap, pos, 8, (100, 100, 100), -1)
            cv2.putText(minimap, node.replace("room_", ""),
                        (pos[0]+12, pos[1]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 100, 100), 1)
        elif step == navigator.current_step + 1:
            # Next destination = yellow blinking circle
            cv2.circle(minimap, pos, 10, (0, 255, 255), 2)
            cv2.putText(minimap, node.replace("room_", ""),
                        (pos[0]+12, pos[1]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
        else:
            # Future nodes = white circle
            cv2.circle(minimap, pos, 8, (255, 255, 255), 1)
            cv2.putText(minimap, node.replace("room_", ""),
                        (pos[0]+12, pos[1]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

    # Legend
    cv2.circle(minimap,  (15, mh-60), 6, (0, 255, 0),     -1)
    cv2.putText(minimap, "Current",   (25, mh-56),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
    cv2.circle(minimap,  (15, mh-40), 6, (0, 255, 255),    1)
    cv2.putText(minimap, "Next",      (25, mh-36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
    cv2.circle(minimap,  (15, mh-20), 6, (100, 100, 100), -1)
    cv2.putText(minimap, "Visited",   (25, mh-16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (100, 100, 100), 1)

    # Paste minimap back onto frame
    frame[margin:margin+mh, w-mw-margin:w-margin] = minimap
    return frame

# ── Draw overlay ───────────────────────────────────────────────────────────
def draw_overlay(frame, ocr_results, navigator, detected_node):
    h, w = frame.shape[:2]

    # Draw OCR boxes
    for (bbox, text, prob) in ocr_results:
        if prob > 0.4:
            import numpy as np
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame, f"{text}({prob:.2f})",
                        (pts[0][0], pts[0][1]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Draw navigation status
    status, color = navigator.get_status()
    cv2.rectangle(frame, (0, 0), (w, 90), (0, 0, 0), -1)
    cv2.putText(frame, status,
                (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Draw progress bar
    progress = navigator.current_step / (len(ROUTE) - 1)
    bar_w    = int(w * progress)
    cv2.rectangle(frame, (0, 60), (w, 80),   (50, 50, 50), -1)
    cv2.rectangle(frame, (0, 60), (bar_w, 80), (0, 255, 0), -1)
    cv2.putText(frame, f"Progress: {navigator.current_step}/{len(ROUTE)-1}",
                (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Show detected node
    if detected_node:
        cv2.putText(frame, f"🔍 Detected: {detected_node}",
                    (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.putText(frame, "Q: Quit",
                (w-100, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return frame

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ Cannot open camera!")
        return

    print("✅ Camera opened!")
    nav         = Navigator()
    frame_count = 0
    ocr_results = []
    detected    = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Run OCR every 5 frames
        if frame_count % 5 == 0:
            results  = reader.readtext(frame)
            ocr_results = results
            texts    = [(r[1], r[2]) for r in results]
            node, text, conf = match_text(texts)

            if node:
                detected = node
                nav.update(node)

        # Draw overlay
        frame = draw_overlay(frame, ocr_results, nav, detected)
        cv2.imshow("NaviGrid Navigation", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()