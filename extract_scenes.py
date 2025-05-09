import os
import shutil
from tkinter import Tk, filedialog
from models.TransNetV2.transnetv2 import TransNetV2
import numpy as np

# Hide Tkinter root window
Tk().withdraw()

################################################################################
# 1️⃣ FILE SELECTION PROMPT
################################################################################

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
os.makedirs(os.path.join(target_folder, "thumbnails"), exist_ok=True)
os.makedirs(os.path.join(target_folder, "outputs"), exist_ok=True)


################################################################################
# 2️⃣ COPY VIDEO INTO DATA FOLDER
################################################################################
print(f"\n")
print(f"- 📂 Copying video to: {target_video_path}")
shutil.copyfile(video_path, target_video_path)

################################################################################
# 3️⃣ RUN TRANSNETV2 AND GENERATE PREDICTIONS
################################################################################
print(f"\n")
print(f"- 🚀 Running TransNetV2 on {target_video_path}")
model = TransNetV2("models/TransNetV2/transnetv2-weights")


# Extract frames and run prediction
video_frames, single_frame_predictions, all_frame_predictions = model.predict_video(target_video_path)

# Save outputs inside the project folder
# Stack single-frame and all-frame predictions side by side
combined_predictions = np.stack((single_frame_predictions, all_frame_predictions), axis=1)
np.savetxt(os.path.join(target_folder, "predictions.txt"), combined_predictions, fmt="%.6f")

np.savetxt(os.path.join(target_folder, "scenes.txt"), model.predictions_to_scenes(single_frame_predictions), fmt="%d")
model.visualize_predictions(video_frames, (single_frame_predictions, all_frame_predictions)).save(
    os.path.join(target_folder, "vis.png")
)



import subprocess

################################################################################
# 4️⃣ THUMBNAIL EXTRACTION
################################################################################
print(f"\n")
print(f"- 🖼️ Extracting thumbnails to: {os.path.join(target_folder, 'thumbnails')}")
with open(os.path.join(target_folder, "scenes.txt"), "r") as f:
    scenes = [line.strip().split() for line in f.readlines()]

for idx, (start, end) in enumerate(scenes):
    start, end = int(start), int(end)
    midpoint = (start + end) // 2

    # Thumbnail filenames
    start_thumb = os.path.join(target_folder, "thumbnails", f"scene_{idx:03d}_start.jpg")
    mid_thumb = os.path.join(target_folder, "thumbnails", f"scene_{idx:03d}_mid.jpg")
    end_thumb = os.path.join(target_folder, "thumbnails", f"scene_{idx:03d}_end.jpg")

    # ffmpeg commands
    for frame, thumb_path in [(start, start_thumb), (midpoint, mid_thumb), (end, end_thumb)]:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", target_video_path,
            "-vf", f"select=eq(n\\,{frame})",
            "-vframes", "1",
            thumb_path
        ]
        print(f"📸 Extracting frame {frame} → {thumb_path}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("✅ Thumbnails successfully saved.")





print(f"\n")
print(f"✅ Finished processing. All results are in: {target_folder}")
print(f"\n")
