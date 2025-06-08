# [Project Name]

This version of the project runs without Docker.  
All source code is located inside the `app/` folder.

---

## Project Structure

```
project/
└── app/
    ├── image-input.py           # Main script that reads input images and sends them to services
    ├── face_landmark_server.py # Service for face landmark detection (uses GRPC and Redis)
    ├── age_gender_server.py    # Service for age and gender detection (uses GRPC and Redis)
    ├── aggregator_server.py    # Final aggregator service that collects results
    ├── config.yaml             # Configuration file for input/output paths
    └── requirements.txt        # Project dependencies
```

---

## Overview

- First, start the two services `face_landmark_server.py` and `age_gender_server.py`.
- Then start the `aggregator_server.py` service.
- Finally, run `image-input.py` which reads the input images and sends requests to the services.
- Input images should be placed in a folder, and the folder path should be specified in `config.yaml`.
- Output files will be saved to the output path specified in `config.yaml`.
- For each processed image, a JSON file will be created containing face bounding box, landmarks, age, and gender information.

---

## Prerequisites

1. **Create and activate a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r app/requirements.txt
```

> ⚠️ **Important:**  
> The `dlib` library requires `cmake` to be installed on your system before installation.  
> - On Ubuntu, install cmake with:  
>   ```bash
>   sudo apt-get install cmake
>   ```  
> - On Windows, download and install cmake from the official website.

---

## Configuration (`config.yaml`)

Specify the input and output directories in `app/config.yaml`:

```yaml
input_folder: "/path/to/input/images"
output_folder: "/path/to/output/folder"
```

---

## Running the Project

1. Start the face landmark detection service:

```bash
python app/face_landmark_server.py
```

2. Start the age and gender detection service:

```bash
python app/age_gender_server.py
```

3. Start the aggregator service:

```bash
python app/aggregator_server.py
```

4. Finally, run the main image input script to process images:

```bash
python app/image-input.py
```

---

## Output

- Processed images with detected faces and landmarks will be saved in the output folder.
- A JSON file for each image containing face bounding boxes, landmarks, age, and gender information will also be generated.

---

## Notes

- For easier setup and dependency management, especially for running multiple services and Redis, consider using the Dockerized version of this project available in the other branch.

---

## Common Issues

- If you encounter problems installing `dlib`, make sure you have installed `cmake` and a C++ compiler (e.g., `build-essential` on Linux).
- Ensure that Redis server is running on your system (or via Docker if applicable).

---

If you want, I can also prepare the README for the Docker branch.

