# SceneMapper

SceneMapper is a toolkit for analyzing video structure using AI-powered shot boundary detection. It helps extract transitions, generate thumbnails, and export timeline references for editing, tagging, or recreating cuts from a reference video.

---

## 🔍 What It Does

- Detects scene changes and transitions using [TransNetV2](https://github.com/soCzech/TransNetV2)
- Extracts thumbnails around detected transitions
- Generates structured CSV/JSON timeline files
- (Optional) Prepares output for use in editing software (e.g., Resolve, Premiere)

---

## 📦 Folder Structure

```
SceneMapper/
├── data/
│   └── [video-name]/
│       ├── input.mov
│       ├── predictions.txt
│       ├── scenes.txt
│       ├── vis.png
│       └── thumbnails/
├── outputs/
│   └── [video-name]_timeline.csv
├── models/
│   └── transnetv2-weights/
├── extract_transitions.py
├── export_timeline.py
├── utils/
│   └── ffmpeg_tools.py
├── main.py
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/SceneMapper.git
cd SceneMapper
```

### 2. Create and activate a Conda environment

```bash
conda create -n SceneMapper python=3.10
conda activate SceneMapper
```

> ⚠️ **Note:**: This assumes a MacOS development enviroment with M Chips

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Place your video

Place your video file in:

```
data/[video-name]/input.mov
```

### 5. Run analysis

```bash
python main.py --video data/[video-name]/input.mov
```

This will:
- Run scene detection
- Generate thumbnails
- Output a structured timeline CSV in `outputs/`

---

### 🔚 To deactivate the environment

```bash
conda deactivate
```

---

## 📚 Dependencies

- Python 3.8+
- TensorFlow (macOS or CPU-only)
- NumPy
- OpenCV
- Pillow
- ffmpeg (installed via `brew`, `apt`, or `choco`)
- ffmpeg-python

> ⚠️ **Note:** You must have `ffmpeg` installed and accessible via terminal.

---

## 🛠️ Credits

Built using [TransNetV2](https://github.com/soCzech/TransNetV2) by Pavel Sofranko.  
Additional tooling and automation by [marcocrio](https://github.com/marcocrio).

---

## 🧪 TODO

- [ ] Add GUI or CLI prompts
- [ ] Support EDL/FCPXML export
- [ ] Add AI captioning for scenes
- [ ] Batch processing of multiple videos
- [ ] Test full pipeline on Linux and Windows
