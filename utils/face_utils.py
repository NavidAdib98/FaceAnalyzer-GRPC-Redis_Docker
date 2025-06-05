import dlib
import cv2
import json
import numpy as np

# Load models once globally
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./models/shape_predictor_68_face_landmarks.dat')
age_net = cv2.dnn.readNetFromCaffe('./models/age-model/age_deploy.prototxt', './models/age-model/age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('./models/gender-model/gender_deploy.prototxt', './models/gender-model/gender_net.caffemodel')

AGE_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
GENDER_LIST = ['Male', 'Female']


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
    color_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    return faces, gray,color_image

# ------------------------------------------------------------------
# ------------------------------------------------------------------
def predict_age_gender_with_padding(image, faces, padding_ratio=0.4):
    """
    Predicts age and gender for each detected face with padding applied.

    Args:
        image (np.ndarray): Original BGR image.
        faces (List[dlib.rectangle]): List of face bounding boxes.
        padding_ratio (float): Fraction of width and height to use as padding (default=0.4)

    Returns:
        List[Dict]: List of dictionaries, each containing:
            - 'box': (x1_pad, y1_pad, x2_pad, y2_pad)
            - 'age': predicted age
            - 'gender': predicted gender
    """
    predictions = []
    h_img, w_img = image.shape[:2]

    for face in faces:
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

        w = x2 - x1
        h = y2 - y1
        pad_x = int(padding_ratio * w)
        pad_y = int(padding_ratio * h)

        # مختصات دارای padding
        x1_pad = max(0, x1 - pad_x)
        y1_pad = max(0, y1 - pad_y)
        x2_pad = min(w_img - 1, x2 + pad_x)
        y2_pad = min(h_img - 1, y2 + pad_y)

        face_img = image[y1_pad:y2_pad, x1_pad:x2_pad].copy()

        # پیش‌بینی با مدل
        blob = cv2.dnn.blobFromImage(face_img, 1.0, (227, 227),
                                     (78.4263377603, 87.7689143744, 114.895847746),
                                     swapRB=False)

        gender_net.setInput(blob)
        gender_preds = gender_net.forward()
        gender = GENDER_LIST[gender_preds[0].argmax()]

        age_net.setInput(blob)
        age_preds = age_net.forward()
        age = AGE_LIST[age_preds[0].argmax()]

        predictions.append({
            'box': (x1_pad, y1_pad, x2_pad, y2_pad),
            'age': age,
            'gender': gender
        })

    return predictions


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

# ------------------------------------------------------------------
# ------------------------------------------------------------------

def draw_combined_annotations(image_bytes, combined_json):
    """
    Draws both facial landmarks and age-gender annotations on the image.

    Args:
        image_bytes (bytes): Input image in bytes.
        combined_json (str or dict): JSON string or parsed dict with:
            {
                "landmarks": [ [ [x,y], ..., [x,y] ], ... ],
                "age_gender": [ { "age": str, "gender": str, "box": [x1,y1,x2,y2] }, ... ]
            }

    Returns:
        np.ndarray: Annotated image (BGR format).
    """
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to decode image bytes.")

    # Parse JSON if it's a string
    if isinstance(combined_json, str):
        combined_data = json.loads(combined_json)
    else:
        combined_data = combined_json

    landmarks_list = combined_data.get("landmarks", [])
    age_gender_list = combined_data.get("age_gender", [])

    # Ensure both lists are of the same length
    if len(landmarks_list) != len(age_gender_list):
        raise ValueError("Mismatch: 'landmarks' and 'age_gender' must have the same number of entries.")

    for i in range(len(landmarks_list)):
        # Draw landmarks
        for (x, y) in landmarks_list[i]:
            cv2.circle(image, (int(x), int(y)), radius=2, color=(0, 255, 0), thickness=-1)

        # Draw age-gender and box
        age = age_gender_list[i].get("age", "?")
        gender = age_gender_list[i].get("gender", "?")
        box = age_gender_list[i].get("box", [0, 0, 0, 0])
        x1, y1, x2, y2 = map(int, box)

        label = f"{gender}, {age}"
        cv2.rectangle(image, (x1, y1), (x2, y2), color=(0, 255, 255), thickness=2)
        cv2.putText(image, label, (x1, y1 - 10), 
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7,
                    color=(0, 255, 0), thickness=2)

    return image
