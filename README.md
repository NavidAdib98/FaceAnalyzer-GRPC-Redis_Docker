# Face Analyzer (GRPC + Redis Version without Docker)

This project is a facial image analyzer pipeline that uses gRPC services and Redis for fast memory sharing. It processes images to detect faces, extract facial landmarks, and estimate age and gender. The final output includes annotated images and structured JSON data describing detected attributes.

## 🔧 Prerequisites

- Python 3.8+
- `cmake` (required for `dlib`)
- Redis server running locally
- Virtual environment (recommended)
- Required Python packages:

```bash
python -m venv venv
source venv/bin/activate     # On Windows use venv\Scripts\activate
pip install -r requirements.txt
```

> ⚠️ `dlib` requires CMake to be installed. On Ubuntu: `sudo apt install cmake`, on macOS: `brew install cmake`.

## 📁 Directory Structure

```
app/
├── aggregator_server.py
├── face_landmark_server.py
├── age_gender_server.py
├── image_input.py
├── config.yaml
├── models/   <-- You must download the required model files manually
```

## 🚀 Execution Order

Make sure Redis is running first.

Then, run the services in the following order **in separate terminals**:

1. **Aggregator Service**  
   Handles final collection and storage of output data.

   ```bash
   python app/aggregator_server.py
   ```

2. **Face Landmark Service**  
   Detects faces and extracts landmark points.

   ```bash
   python app/face_landmark_server.py
   ```

3. **Age & Gender Service**  
   Estimates age and gender based on face crops.

   ```bash
   python app/age_gender_server.py
   ```

4. **Image Input Script**  
   Feeds input images and coordinates the pipeline.

   ```bash
   python app/image_input.py
   ```

## ⚙️ Configuration

Edit the `app/config.yaml` file to define:

- Input image folder path
- Output folder for:
  - Annotated images
  - Output `.json` files

## 🧠 Output

- Images with detected faces, landmarks, and annotations for age/gender
- A corresponding `.json` file per image with detailed analysis

<h2>Examples :</h2>
    
<img src="example/SingleFace.jpg_1550cfb2bbf1deba53539684230dfcac10933bd37fcaacc6ef0a663cb8592eb0.jpg">
<img src="example/MultipleFaces.jpg_1e9d7f27def820bfa538fbff1175826275cd392ac63d222d23b4f2cd16fb1661.jpg">
Warning: Sometimes the model can be a bit cheeky and mistake gender—don’t worry, it’s just having a little fun! 😄

## 📦 Models

Due to GitHub file size limitations, the model files are **not included** in the repository.

Please manually download and place the following files:

- `shape_predictor_68_face_landmarks.dat` → `app/models/`
- `age_net.caffemodel` → `app/models/age-model/`
- `gender_net.caffemodel` → `app/models/gender-model/`

Make sure the directories `age-model` and `gender-model` exist inside the `models` folder.

