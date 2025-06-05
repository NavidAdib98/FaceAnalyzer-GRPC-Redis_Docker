import dlib
import cv2
import json
import numpy as np

# Load models once globally
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./models/shape_predictor_68_face_landmarks.dat')

# ------------------------------------------------------------------
# ------------------------------------------------------------------
def detect_faces(image_bytes):
    """
    Detects faces in the given image.

    Args:
        image_bytes (bytes): The image in byte format (e.g., received via gRPC).

    Returns:
        Tuple[List[dlib.rectangle], np.ndarray]: A list of detected face rectangles and the grayscale image.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    return faces, gray

# ------------------------------------------------------------------
# ------------------------------------------------------------------
def extract_landmarks(gray_image, faces):
    """
    Extracts 68 facial landmarks for each detected face.

    Args:
        gray_image (np.ndarray): The grayscale version of the original image.
        faces (List[dlib.rectangle]): List of face bounding boxes.

    Returns:
        List[List[Tuple[int, int]]]: A list of landmark coordinates for each face.
    """
    all_landmarks = []
    for face in faces:
        shape = predictor(gray_image, face)
        landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]
        all_landmarks.append(landmarks)
    return all_landmarks


# ------------------------------------------------------------------
# ------------------------------------------------------------------
def draw_landmarks_on_image(image_bytes, landmarks_json):
    """
    Draw landmarks on the given image.

    Args:
        image_bytes (bytes): Input image in bytes.
        landmarks_json (str or dict): JSON string or parsed dict containing landmarks.
            Expected format:
            [
                [[x1, y1], [x2, y2], ..., [x68, y68]],  # for face 1
                [[x1, y1], ..., [x68, y68]]             # for face 2, ...
            ]

    Returns:
        np.ndarray: Image with landmarks drawn (in BGR format).
    """
    # Decode image from bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Parse JSON if necessary
    if isinstance(landmarks_json, str):
        landmarks_data = json.loads(landmarks_json)
    else:
        landmarks_data = landmarks_json

    # Draw landmarks for each face
    for face_landmarks in landmarks_data:
        for (x, y) in face_landmarks:
            cv2.circle(image, (int(x), int(y)), radius=2, color=(0, 255, 0), thickness=-1)

    return image