import os
import shutil
import subprocess
import argparse
from tkinter import Tk, filedialog, messagebox
from models.TransNetV2.transnetv2 import TransNetV2
import numpy as np
import datetime
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import librosa

# Hide Tkinter root window
Tk().withdraw()

################################################################################
# 1️⃣ ARGUMENT PARSING
################################################################################
parser = argparse.ArgumentParser(description="Extract scenes and thumbnails from a video.")
parser.add_argument("-t", "--thumbnails", type=int, default=3, help="Number of thumbnails per scene (default: 3)")
parser.add_argument("-o", "--open", action="store_true", help="Open the folder after processing")
parser.add_argument("-l", "--log", action="store_true", help="Save the thumbnail extraction log")
parser.add_argument("-n", "--num-threads", type=int, default=8, help="Number of threads for thumbnail extraction (default: 8)")
parser.add_argument("-r", "--replace", action="store_true", help="Automatically replace the video file if it exists.")
parser.allow_abbrev = True
args = parser.parse_args()

# Timestamp for unique folder names if --keep-history is used
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_entries = []

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
video_ext = os.path.splitext(video_path)[1]
target_folder = os.path.join("projects", video_name)
target_video_path = os.path.join(target_folder, f"{video_name}{video_ext}")

# Prepare all subfolders
os.makedirs(os.path.join(target_folder, "outputs", "thumbnails"), exist_ok=True)
os.makedirs(os.path.join(target_folder, "outputs"), exist_ok=True)

################################################################################
# 🚫 BLOCKING ALERT LOGIC
################################################################################
if os.path.exists(target_video_path):
    if args.replace:
        print("⚠️ Replacing existing file.")
    else:
        root = Tk()
        root.withdraw()
        result = messagebox.askyesnocancel("File Exists", "The file already exists. Replace it?")
        root.update()
        root.destroy()
        if result is None:
            print("❌ Operation cancelled.")
            sys.exit(0)
        elif result:
            print("⚠️ Replacing existing file.")
        else:
            print("✅ Using the existing file.")

################################################################################
# 2️⃣ COPY VIDEO INTO PROJECT FOLDER
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
# 4️⃣ AUDIO EXTRACTION AND BPM ANALYSIS
################################################################################
try:
    print("\n- 🎵 Extracting audio and analyzing BPM...")
    audio_path = os.path.join(target_folder, "outputs", "audio.wav")
    if os.path.exists(audio_path):
        print("⚠️ Existing audio file found. Deleting before extraction.")
        os.remove(audio_path)

    subprocess.run([
        "ffmpeg", "-i", target_video_path, 
        "-vn", "-acodec", "pcm_s16le", 
        "-ar", "44100", "-ac", "2", audio_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    print(f"\n🎵 BPM Detected: {tempo}\n")
    log_entries.append(f"BPM Detected: {tempo}")
except Exception as e:
    print(f"⚠️ Audio processing failed: {e}")
    log_entries.append(f"Audio processing failed: {e}")

################################################################################
# 5️⃣ THUMBNAIL EXTRACTION (Multithreaded + Progress Bar)
################################################################################
print(f"\n")
print(f"- 🖼️ Extracting thumbnails to: {os.path.join(target_folder, 'outputs', 'thumbnails')}")

def extract_thumbnail(frame, thumb_path):
    """ Extract a single thumbnail. """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", target_video_path,
        "-vf", f"select=eq(n\\,{frame})",
        "-vframes", "1",
        thumb_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Load scenes and extract thumbnails
with open(os.path.join(target_folder, "outputs", "scenes.txt"), "r") as f:
    scenes = [line.strip().split() for line in f.readlines()]

tasks = []
with ThreadPoolExecutor(max_workers=args.num_threads) as executor:
    with tqdm(total=len(scenes) * args.thumbnails, desc="📸 Extracting Thumbnails", unit="thumb") as pbar:
        for idx, (start, end) in enumerate(scenes):
            step = max(1, (int(end) - int(start)) // (args.thumbnails - 1))
            frames = list(range(int(start), int(end), step))[:args.thumbnails]
            if len(frames) < args.thumbnails:
                frames.append(int(end))

            for i, frame in enumerate(frames):
                thumb_path = os.path.join(target_folder, "outputs", "thumbnails", f"scene_{idx:03d}_{i}.jpg")
                future = executor.submit(extract_thumbnail, frame, thumb_path)
                tasks.append(future)
        
        for future in as_completed(tasks):
            pbar.update(1)

print("\n✅ Thumbnails successfully saved.")

################################################################################
# 6️⃣ OPEN THE FOLDER IF SPECIFIED
################################################################################
if args.open:
    print(f"\n🗂️ Opening folder: {target_folder}")
    subprocess.run(["open", target_folder])

print(f"\n✅ Finished processing. All results are in: {target_folder}\n")
