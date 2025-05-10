import os
import csv
import json
import ffmpeg
import subprocess
import argparse

################################################################################
# 1️⃣ ARGUMENT PARSING
################################################################################
parser = argparse.ArgumentParser(description="Export timeline from processed video data.")
parser.add_argument("--folder", type=str, required=True, help="Name of the video folder to process.")
args = parser.parse_args()

# Extract video name from argument
video_name = args.folder
target_folder = os.path.join("data", video_name)
output_folder = os.path.join(target_folder, "outputs")

print(f"\n🎥 Video selected: {video_name}")
print(f"📁 Project folder: {output_folder}")

# Check for processed files in outputs
scenes_file = os.path.join(output_folder, "scenes.txt")
predictions_file = os.path.join(output_folder, "predictions.txt")
vis_file = os.path.join(output_folder, "vis.png")

# If they don't exist, we exit gracefully
if not all(os.path.exists(f) for f in [scenes_file, predictions_file, vis_file]):
    print(f"❌ Required files not found in {output_folder}. Has the video been processed?")
    exit(1)

# Read scenes.txt
with open(scenes_file, "r") as f:
    scenes = [line.strip().split() for line in f.readlines()]

# Extract metadata with ffmpeg
try:
    video_path = os.path.join(target_folder, "input.mov")
    probe = ffmpeg.probe(video_path)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    fps = eval(video_info['r_frame_rate'])
    duration = float(video_info['duration'])
    width = video_info['width']
    height = video_info['height']
except Exception as e:
    print(f"❌ Failed to retrieve video metadata: {e}")
    exit(1)

print(f"\n🎥 Video Info:")
print(f" - Resolution: {width}x{height}")
print(f" - FPS: {fps}")
print(f" - Duration: {duration} seconds")

# Convert frames to timestamps
def frame_to_timestamp(frame, fps):
    seconds = frame / fps
    millis = int((seconds - int(seconds)) * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"

timeline_data = []

for idx, (start_frame, end_frame) in enumerate(scenes):
    start_frame, end_frame = int(start_frame), int(end_frame)
    midpoint_frame = (start_frame + end_frame) // 2

    timeline_data.append({
        "Scene Number": idx + 1,
        "Start Frame": start_frame,
        "End Frame": end_frame,
        "Midpoint Frame": midpoint_frame,
        "Start Time": frame_to_timestamp(start_frame, fps),
        "End Time": frame_to_timestamp(end_frame, fps),
        "Midpoint Time": frame_to_timestamp(midpoint_frame, fps)
    })

# Save CSV
csv_file = os.path.join(output_folder, "timeline.csv")
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=timeline_data[0].keys())
    writer.writeheader()
    writer.writerows(timeline_data)
print(f"\n✅ CSV Timeline saved to: {csv_file}")

# Save JSON
json_file = os.path.join(output_folder, "timeline.json")
with open(json_file, 'w') as file:
    json.dump(timeline_data, file, indent=4)
print(f"\n✅ JSON Timeline saved to: {json_file}")

# # Open the folder after processing
# print(f"\n🗂️ Opening folder: {output_folder}")
# subprocess.run(["open", output_folder])

print(f"\n✅ Finished exporting timeline. All results are in: {output_folder}\n")
