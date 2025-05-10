import os
import shutil
import subprocess
import argparse
from tkinter import Tk, filedialog
from models.TransNetV2.transnetv2 import TransNetV2
import numpy as np
import datetime
import sys

# Hide Tkinter root window
Tk().withdraw()

################################################################################
# 1️⃣ ARGUMENT PARSING
################################################################################
parser = argparse.ArgumentParser(description="Extract scenes and thumbnails from a video.")
parser.add_argument("-t", "--thumbnails", type=int, default=3, help="Number of thumbnails per scene (default: 3)")
parser.add_argument("-o", "--open", action="store_true", help="Open the folder after processing")
parser.add_argument("-l", "--log", action="store_true", help="Save the thumbnail extraction log")
parser.add_argument("--keep-history", action="store_true", help="Keep a timestamped folder of thumbnails instead of overwriting")
parser.allow_abbrev = True
args = parser.parse_args()

# Timestamp for unique folder names if --keep-history is used
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

print(f"\n")
print("- 🔎 Select the video file to process:")
video_path = filedialog.askopenfilename(
    title="Select Video File",
    filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi *.flv")]
)

if not video_path:
    print(f"\n")
    print("❌ No file selected. Exiting.")
    exit(1)

# Extract video name and prepare paths
video_name = os.path.splitext(os.path.basename(video_path))[0]
target_folder = os.path.join("data", video_name)
target_video_path = os.path.join(target_folder, "input.mov")

# Prepare all subfolders
os.makedirs(os.path.join(target_folder, "outputs" ,"thumbnails"), exist_ok=True)
os.makedirs(os.path.join(target_folder, "outputs"), exist_ok=True)

# Thumbnail folder logic
if args.keep_history:
    thumbnail_folder = os.path.join(target_folder, "outputs", "thumbnails", f"{timestamp}")
    os.makedirs(thumbnail_folder, exist_ok=True)
else:
    thumbnail_folder = os.path.join(target_folder, "outputs", "thumbnails")
    for f in os.listdir(thumbnail_folder):
        path_to_delete = os.path.join(thumbnail_folder, f)
        if os.path.isfile(path_to_delete):
            os.remove(path_to_delete)
        elif os.path.isdir(path_to_delete):
            shutil.rmtree(path_to_delete)


################################################################################
# 2️⃣ COPY VIDEO INTO DATA FOLDER
################################################################################
print(f"\n")
print(f"- 📂 Copying video to: {target_video_path}")
shutil.copyfile(video_path, target_video_path)

################################################################################
# 3️⃣ RUN TRANSNETV2 AND GENERATE PREDICTIONS
################################################################################
try:
    print(f"\n")
    print(f"- 🚀 Running TransNetV2 on {target_video_path}")
    model = TransNetV2("models/TransNetV2/transnetv2-weights")

    # Extract frames and run prediction
    video_frames, single_frame_predictions, all_frame_predictions = model.predict_video(target_video_path)

    # Save outputs inside the project folder
    combined_predictions = np.stack((single_frame_predictions, all_frame_predictions), axis=1)
    np.savetxt(os.path.join(target_folder, "outputs", "predictions.txt"), combined_predictions, fmt="%.6f")
    np.savetxt(os.path.join(target_folder, "outputs", "scenes.txt"), model.predictions_to_scenes(single_frame_predictions), fmt="%d")
    model.visualize_predictions(video_frames, (single_frame_predictions, all_frame_predictions)).save(
        os.path.join(target_folder, "outputs", "vis.png")
    )

except Exception as e:
    log_file = os.path.join(target_folder, "outputs", "error.log")
    with open(log_file, "w") as log:
        log.write(f"[{datetime.datetime.now()}] Error: {str(e)}\n")
    print(f"❌ An error occurred. Check {log_file} for details.")
    exit(1)

################################################################################
# 4️⃣ THUMBNAIL EXTRACTION
################################################################################
print(f"\n")
print(f"- 🖼️ Extracting thumbnails to: {thumbnail_folder}")

log_entries = []

def extract_thumbnails(start, end, idx):
    """ Extracts thumbnails evenly spaced between start and end frames. """
    step = max(1, (end - start) // (args.thumbnails - 1))
    frames = list(range(start, end, step))[:args.thumbnails]
    if len(frames) < args.thumbnails:
        frames.append(end)

    for i, frame in enumerate(frames):
        thumb_path = os.path.join(thumbnail_folder, f"scene_{idx:03d}_{i}.jpg")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-i", target_video_path,
            "-vf", f"select=eq(n\\,{frame})",
            "-vframes", "1",
            thumb_path
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log_entries.append(f"[{datetime.datetime.now()}] Extracted scene {idx} frame {i} → {thumb_path}\n")
            percent_complete = round(((idx * args.thumbnails + i + 1) / (len(scenes) * args.thumbnails)) * 100, 2)
            print(f"\r📸 [{percent_complete}%] Processing thumbnails... ", end="")
        except KeyboardInterrupt:
            print("\n🛑 Process interrupted by user. Exiting gracefully.")
            if args.log:
                log_file = os.path.join(target_folder, "outputs", f"thumbnail_log_{timestamp}.txt")
                with open(log_file, "w") as log:
                    log.writelines(log_entries)
                print(f"💾 Partial log saved to {log_file}")
            exit(1)

# Load scenes and extract thumbnails
with open(os.path.join(target_folder, "outputs", "scenes.txt"), "r") as f:
    scenes = [line.strip().split() for line in f.readlines()]

for idx, (start, end) in enumerate(scenes):
    extract_thumbnails(int(start), int(end), idx)

print("\n✅ Thumbnails successfully saved.")

################################################################################
# 5️⃣ AUTO-CALL EXPORT TIMELINE
################################################################################
# Auto-call export_timeline.py
print("\n📌 Calling `export_timeline.py` to generate CSV and JSON...")
try:
    subprocess.run(["python", "export_timeline.py", "--folder", video_name], check=True)
    print("\n✅ Timeline export completed.")
except Exception as e:
    print(f"❌ Timeline export failed: {e}")


################################################################################
# 6️⃣ OPEN THE FOLDER IF SPECIFIED
################################################################################
if args.open:
    print(f"\n🗂️ Opening folder: {target_folder}")
    subprocess.run(["open", target_folder])

print(f"\n✅ Finished processing. All results are in: {target_folder}\n")
