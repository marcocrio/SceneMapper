import os
import csv
import argparse
from tkinter import Tk, filedialog
import datetime

# Hide Tkinter root window
Tk().withdraw()

################################################################################
# 1️⃣ ARGUMENT PARSING
################################################################################
parser = argparse.ArgumentParser(description="Export timeline data as CSV, JSON, and EDL.")
parser.add_argument("-t", "--template", action="store_true", help="Generate template EDL with placeholder clip names")
parser.add_argument("-f", "--framerate", type=float, default=None, help="Override the framerate for the EDL export")
parser.add_argument("--folder", type=str, required=True, help="Specify the folder name of the project")
parser.allow_abbrev = True
args = parser.parse_args()

################################################################################
# 2️⃣ SELECT VIDEO FOLDER
################################################################################
project_folder = os.path.join("projects", args.folder)
output_folder = os.path.join(project_folder, "outputs")

predictions_path = os.path.join(output_folder, "predictions.txt")
scenes_path = os.path.join(output_folder, "scenes.txt")
edl_path = os.path.join(output_folder, "timeline.edl")

if not os.path.exists(predictions_path) or not os.path.exists(scenes_path):
    print("❌ Missing required files (predictions.txt or scenes.txt).")
    exit(1)

################################################################################
# 3️⃣ VIDEO INFORMATION
################################################################################
print(f"\n🎥 Video selected: {args.folder}")
print(f"📁 Project folder: {project_folder}")

# Default framerate is set to 24 if not provided
framerate = args.framerate if args.framerate else 24
print(f"🎞️ Using framerate: {framerate} fps")

################################################################################
# 4️⃣ CREATE EDL FILE
################################################################################
print(f"\n📝 Generating EDL file: {edl_path}")

def timecode_from_frame(frame, framerate):
    hours = int(frame // (3600 * framerate))
    minutes = int((frame % (3600 * framerate)) // (60 * framerate))
    seconds = int((frame % (60 * framerate)) // framerate)
    frames = int(frame % framerate)
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

# Read scenes
with open(scenes_path, "r") as f:
    scenes = [list(map(int, line.strip().split())) for line in f.readlines()]

# EDL Header
with open(edl_path, "w") as edl:
    edl.write(f"TITLE: {args.folder}\n")
    edl.write(f"FCM: NON-DROP FRAME\n")

    record_frame = 0  # Starting from absolute zero
    for idx, (start, end) in enumerate(scenes):
        clip_name = f"Clip_{idx + 1:02d}" if args.template else f"{args.folder}.mov"
        
        tc_in = timecode_from_frame(start, framerate)
        tc_out = timecode_from_frame(end, framerate)
        
        duration = end - start
        tc_rec_in = timecode_from_frame(record_frame, framerate)
        record_frame += duration  # Increment by the actual scene duration
        tc_rec_out = timecode_from_frame(record_frame, framerate)

        edl.write(f"\n{idx + 1:04d}  AX       V     C        {tc_in} {tc_out} {tc_rec_in} {tc_rec_out}\n")
        edl.write(f"* FROM CLIP NAME: {clip_name}\n")
        edl.write(f"* COMMENT: Scene {idx + 1} - Hard Cut\n")

print("\n✅ EDL Generation Complete.")
print(f"📝 EDL saved to: {edl_path}")
print("\n✅ Finished processing. All results are in the outputs folder.\n")
