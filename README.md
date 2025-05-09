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
│       ├── input.mov               # Original video file
│       ├── predictions.txt         # Transition scores
│       ├── scenes.txt              # Detected scene boundaries
│       ├── vis.png                 # Visualization of transitions
│       ├── thumbnails/             # Thumbnails of key transitions
│       │   ├── frame_0001.jpg
│       │   └── frame_0002.jpg
│       └── outputs/                # All exported files for Resolve, Premiere, etc.
│           ├── [video-name]_timeline.csv
│           └── [video-name]_timeline.xml
├── models/
│   └── TransNetV2/
│       ├── transnetv2.py
│       ├── transnetv2-weights/
│       │   ├── saved_model.pb
│       │   └── variables/
│       │       ├── variables.data-00000-of-00001
│       │       └── variables.index
│       └── LICENSE
├── utils/
│   └── ffmpeg_tools.py
├── extract_transitions.py
├── export_timeline.py
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

> ⚠️ **Note**: This assumes a macOS development environment with Apple Silicon chips.

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

### 🔄 Updating the TransNetV2 model (weights or code)

To update the model or pull latest changes from upstream:

```bash
cd models/TransNetV2
git pull origin master
```

> This works if the folder was initialized with Git sparse-checkout.  
> If not, follow the setup steps from `scripts/setup_transnetv2.sh` (coming soon).

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

- Built using [TransNetV2](https://github.com/soCzech/TransNetV2) by Pavel Sofranko, used under the Apache 2.0 License.
- The model and weights are located in `models/TransNetV2/`.
- Additional tooling and automation by [marcocrio](https://github.com/marcocrio).

---

## 🧪 TODO

- [ ] Add Instructions for other OS.
- [ ] Add GUI or CLI prompts
- [ ] Support EDL/FCPXML export
- [ ] Add AI captioning for scenes
- [ ] Batch processing of multiple videos
- [ ] Test full pipeline on Linux and Windows







