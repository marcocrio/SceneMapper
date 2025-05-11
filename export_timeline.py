import os
import argparse
import ffmpeg
import pandas as pd
import json
from tkinter import Tk, filedialog

# Hide Tkinter root window
Tk().withdraw()

################################################################################
# 1️⃣ ARGUMENT PARSING
################################################################################
parser = argparse.ArgumentParser(description="Export timeline as CSV and JSON with metadata.")
parser.add_argument("--folder", type=str, required=True, help="Project folder name")
parser.add_argument("--ext", type=str, required=True, help="File extension of the video")
parser.allow_abbrev = True
args = parser.parse_args()

# Prepare paths
folder_name = args.folder
video_extension = args.ext
folder_path = os.path.join("projects", folder_name, "outputs")
video_path = os.path.join("projects", folder_name, f"{folder_name}.{video_extension}")

# Validate existence
if not os.path.exists(video_path):
    print(f"❌ Video file not found: {video_path}")
    exit(1)

# Output paths
csv_path = os.path.join(folder_path, "timeline.csv")
json_path = os.path.join(folder_path, "timeline.json")

################################################################################
# 2️⃣ VIDEO METADATA EXTRACTION
################################################################################
print("\n🎥 Video selected:", folder_name)
print(f"📁 Project folder: {folder_path}")

# Get video metadata
try:
    probe = ffmpeg.probe(video_path)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    resolution = f"{video_info['width']}x{video_info['height']}"
    fps = eval(video_info['r_frame_rate'])
    duration = float(probe['format']['duration'])

    print("\n🎥 Video Info:")
    print(f" - Resolution: {resolution}")
    print(f" - FPS: {fps}")
    print(f" - Duration: {duration} seconds")

except Exception as e:
    print(f"❌ Failed to retrieve video metadata: {e}")
    exit(1)

################################################################################
# 3️⃣ SCENES LOADING AND DATAFRAME CREATION
################################################################################
scenes_path = os.path.join(folder_path, "scenes.txt")

if not os.path.exists(scenes_path):
    print(f"❌ Scenes file not found: {scenes_path}")
    exit(1)

# Load scenes
print("\n🔍 Loading scenes from:", scenes_path)
scenes = []
with open(scenes_path, "r") as f:
    for idx, line in enumerate(f):
        start, end = map(int, line.strip().split())
        scenes.append({
            "Scene": idx + 1,
            "Start Frame": start,
            "End Frame": end,
            "Start Time": f"{start / fps:.2f}",
            "End Time": f"{end / fps:.2f}",
            "Duration (s)": f"{(end - start) / fps:.2f}"
        })

# Create DataFrame
df = pd.DataFrame(scenes)

################################################################################
# 4️⃣ EXPORT TO CSV AND JSON
################################################################################
print("\n💾 Saving timeline to CSV and JSON...")
df.to_csv(csv_path, index=False)
with open(json_path, "w") as json_file:
    json.dump({
        "metadata": {
            "resolution": resolution,
            "fps": fps,
            "duration": duration,
        },
        "scenes": scenes
    }, json_file, indent=4)

print(f"\n✅ Timeline exported:")
print(f" - CSV: {csv_path}")
print(f" - JSON: {json_path}")
print(f"\n✅ Finished processing. All results are in the outputs folder.")
