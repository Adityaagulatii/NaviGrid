🗺️ NaviGrid \
Camera-based indoor navigation — no beacons, no 3D mapping, just your phone.

🎬 Watch NaviGrid in action: \
[Demo](https://vimeo.com/1168262894?share=copy&fl=sv&fe=ci)

📌 Overview
- Eliminates the need for expensive indoor navigation infrastructure 
- No BLE beacons, no Wi-Fi triangulation systems, no 3D building scans 
- Users take a photo of a floorplan and annotate the rooms they want to navigate between 
- Uses Computer Vision and OCR to understand the layout 
- Determines current location, calculates an optimal route, and delivers turn-by-turn directions
- Navigating any new indoor space is as simple as snapping a photo

💡 Inspiration
- Indoor navigation has countless real-world applications — campus wayfinding, robotics, drone delivery, and accessibility for blind and visually impaired individuals
-Current solutions are long, complex, and expensive, typically requiring:
        Deployment of hardware like BLE beacons or Wi-Fi access points
        Full 3D models of the facility
        All because GPS simply doesn't work indoors
- Existing research inspired this project:
          Floorplan2Guide — uses LLMs to parse floorplans for blind and low-vision (BLV) navigation [link](https://arxiv.org/abs/2512.12177)
          Snap&Nav — a smartphone-based system that analyzes floor maps and detects intersections for indoor guidance [link](https://dl.acm.org/doi/10.1145/3676522)
- Both prior systems were still complex and resource-heavy
        NaviGrid's goal: strip indoor navigation down to its simplest form — no beacons, no 3D mapping, no expensive infrastructure, just your camera

\
⚙️ How It Works \
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

\
🎯 Use Cases \
🎓 Campus Navigation — Help new students find classrooms, offices, and facilities \
♿ Accessibility — Empower blind and visually impaired individuals to navigate independently \
🤖 Robotics — Provide autonomous systems with a lightweight indoor mapping solution \
🚁 Drone Delivery — Enable path planning for indoor drone navigation systems

\
🗂️ Project Structure
NaviGrid \
├── lower_level \
│   ├── nodes.py                # Step 1: Load floorplan image + annotations → extract nodes \
│   ├── edges.py                # Step 2: Connect nodes by defining edges/paths \
│   └── navigate.py             # Step 3: Run navigation on lower level floor \
│
├── first_floor \
│   ├── nodes.py                # Step 1: Load floorplan image + annotations → extract nodes \
│   ├── edges.py                # Step 2: Connect nodes by defining edges/paths \
│   └── navigate.py             # Step 3: Run navigation on first floor \
│
├── full_navigation.py          # Full multi-floor navigation pipeline \
├── requirements.txt            # Python dependencies \
└── README.md


