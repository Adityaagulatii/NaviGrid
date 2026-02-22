NaviGrid 🗺️

Camera-based indoor navigation — no beacons, no 3D mapping, just your phone.


What it does
NaviGrid simplifies indoor navigation by eliminating the need for expensive hardware like BLE beacons, Wi-Fi triangulation systems, or 3D building scans. Users simply take a picture of a building's floorplan, annotate the rooms they want to navigate between, and the app uses Computer Vision and OCR to understand the layout and determine their current location. From there, NaviGrid calculates a route and provides turn-by-turn directions — making navigating any new indoor space as easy as snapping a photo.

Inspiration
Indoor navigation has countless real-world applications — helping new students find their way around campus, enabling robotics and drone delivery systems, and improving accessibility for blind and visually impaired individuals. However, the current process is long, complex, and expensive. Traditional indoor navigation requires deploying hardware like BLE beacons or Wi-Fi access points to locate a person, and often demands a full 3D model of the building — all because GPS simply doesn't work indoors.
We came across research tackling this problem — Floorplan2Guide, which uses LLMs to parse floorplans for blind and low-vision navigation, and Snap&Nav, a smartphone-based system that analyzes floor maps and detects intersections for indoor guidance. While impressive, both systems were still quite complex and resource-heavy.
That's what inspired NaviGrid — we wanted to cut down the entire indoor navigation process and make it as simple as possible. No beacons, no 3D mapping, no expensive infrastructure. Just your camera.
Research References:

Floorplan2Guide: LLM-Guided Floorplan Parsing for BLV Indoor Navigation
Snap&Nav: Smartphone-based Indoor Navigation System For Blind People via Floor Map Analysis and Intersection Detection


How it works

Take a photo of the building's floorplan
Annotate the rooms you want to navigate between
NaviGrid parses the floorplan using Computer Vision and OCR
A routing graph is built from the annotated nodes and edges
Turn-by-turn directions are provided to guide you to your destination


Use Cases

🎓 New students navigating a college campus
♿ Accessibility for blind and visually impaired individuals
🤖 Robotics and autonomous systems
🚁 Drone delivery path planning


Tech Stack

Python — core navigation logic
Computer Vision / OCR — floorplan parsing and location detection
Graph-based pathfinding — routing between annotated nodes and edges
