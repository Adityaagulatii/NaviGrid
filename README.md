🗺️ NaviGrid
Camera-based indoor navigation — no beacons, no 3D mapping, just your phone.

🎬 Watch NaviGrid in action:
[Demo](https://vimeo.com/1168262894?share=copy&fl=sv&fe=ci)

📌 Overview
NaviGrid simplifies indoor navigation by eliminating the need for expensive infrastructure. No BLE beacons. No Wi-Fi triangulation systems. No 3D building scans.
Users simply take a picture of a floorplan, annotate the rooms they want to navigate between, and NaviGrid handles the rest — using Computer Vision and OCR to understand the layout, determine the current location, calculate an optimal route, and deliver turn-by-turn directions.

Navigating any new indoor space is now as simple as snapping a photo.


💡 Inspiration
Indoor navigation has countless real-world applications — from helping new students find their way around campus, to enabling robotics and drone delivery systems, to improving accessibility for blind and visually impaired individuals.
Yet the current process is long, complex, and expensive. Traditional indoor navigation requires:

Deploying hardware like BLE beacons or Wi-Fi access points
Building full 3D models of the facility
All because GPS simply doesn't work indoors

We came across research tackling this exact problem:

Floorplan2Guide — uses LLMs to parse floorplans for blind and low-vision (BLV) navigation
Snap&Nav — a smartphone-based system that analyzes floor maps and detects intersections for indoor guidance

While impressive, both systems were still complex and resource-heavy. That's what inspired NaviGrid — we wanted to strip the entire indoor navigation process down to its simplest form.
No beacons. No 3D mapping. No expensive infrastructure. Just your camera.

⚙️ How It Works
📸 Step 1 — Capture
        Take a photo of the building's floorplan

✏️ Step 2 — Annotate
        Mark the rooms or points you want to navigate between

🧠 Step 3 — Parse
        NaviGrid processes the floorplan using Computer Vision and OCR

🕸️ Step 4 — Build Graph
        A routing graph is constructed from annotated nodes and edges

🧭 Step 5 — Navigate
        Turn-by-turn directions guide you to your destination

🎯 Use Cases

🎓 Campus Navigation — Help new students find classrooms, offices, and facilities
♿ Accessibility — Empower blind and visually impaired individuals to navigate independently
🤖 Robotics — Provide autonomous systems with a lightweight indoor mapping solution
🚁 Drone Delivery — Enable path planning for indoor drone navigation systems


🛠️ Tech Stack
ComponentTechnologyCore LogicPythonFloorplan ParsingComputer Vision (OpenCV) + OCR (Tesseract / EasyOCR)PathfindingGraph-based routing (NetworkX)Annotation Interface(specify your UI framework here)
