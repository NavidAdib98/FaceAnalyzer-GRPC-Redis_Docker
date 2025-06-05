import cv2
import dlib
import cv2
import numpy as np

# مدل‌ها را بارگذاری کن
age_net = cv2.dnn.readNetFromCaffe('./models/age-model/age_deploy.prototxt', './models/age-model/age_net.caffemodel')
gender_net = cv2.dnn.readNetFromCaffe('./models/gender-model/gender_deploy.prototxt', './models/gender-model/gender_net.caffemodel')

AGE_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
GENDER_LIST = ['Male', 'Female']



detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./models/shape_predictor_68_face_landmarks.dat")

img = cv2.imread("../data/SingleFace3.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faces = detector(gray)
print(f"Found {len(faces)} face(s)")

for face in faces:
    landmarks = predictor(gray, face)
    for n in range(68):
        x = landmarks.part(n).x
        y = landmarks.part(n).y
        cv2.circle(img, (x, y), 2, (0, 255, 0), -1)

# cv2.imshow("Landmarks", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# # Save result if you want
# cv2.imwrite("output_landmarks.jpg", img)




def predict_age_gender(face_img):
    """
    face_img: تصویر برش خورده صورت (BGR)
    خروجی: پیش‌بینی سن و جنسیت
    """

    blob = cv2.dnn.blobFromImage(face_img, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)

    # پیش‌بینی جنسیت
    gender_net.setInput(blob)
    gender_preds = gender_net.forward()
    gender = GENDER_LIST[gender_preds[0].argmax()]
    

    # پیش‌بینی سن
    age_net.setInput(blob)
    age_preds = age_net.forward()
    age = AGE_LIST[age_preds[0].argmax()]

    return age, gender


for face in faces:
    x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

    # اعمال padding نسبی (مثلاً 40٪ از ارتفاع و عرض چهره)
    w = x2 - x1
    h = y2 - y1
    pad_x = int(0.4 * w)
    pad_y = int(0.4 * h)

    # جلوگیری از بیرون‌زدگی از تصویر
    x1_pad = max(0, x1 - pad_x)
    y1_pad = max(0, y1 - pad_y)
    x2_pad = min(img.shape[1] - 1, x2 + pad_x)
    y2_pad = min(img.shape[0] - 1, y2 + pad_y)

    # استخراج صورت با padding
    face_img = img[y1_pad:y2_pad, x1_pad:x2_pad].copy()

    age, gender = predict_age_gender(face_img)
    print(f"Predicted Age: {age}, Gender: {gender}")

    # رسم روی تصویر
    label = f"{gender}, {age}"
    cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    # 🔵 مستطیل آبی: صورت اصلی
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # 🟢 مستطیل سبز: صورت با padding
    cv2.rectangle(img, (x1_pad, y1_pad), (x2_pad, y2_pad), (0, 255, 0), 2)

cv2.imshow("Age & Gender Estimation", img)
cv2.waitKey(0)
cv2.destroyAllWindows()