import cv2
import dlib

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./models/shape_predictor_68_face_landmarks.dat")

img = cv2.imread("../data/MultipleFaces.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

faces = detector(gray)
print(f"Found {len(faces)} face(s)")

for face in faces:
    landmarks = predictor(gray, face)
    for n in range(68):
        x = landmarks.part(n).x
        y = landmarks.part(n).y
        cv2.circle(img, (x, y), 2, (0, 255, 0), -1)

cv2.imshow("Landmarks", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save result if you want
cv2.imwrite("output_landmarks.jpg", img)