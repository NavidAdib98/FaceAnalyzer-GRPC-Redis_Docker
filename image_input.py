import os
import time
import sys
import grpc
from pathlib import Path

from generated import face_landmark_pb2
from generated import age_gender_pb2
from generated import age_gender_pb2_grpc
from generated import face_landmark_pb2_grpc

# ------- environment variables ---------
DATA_DIR = os.environ.get("DATA_DIR", "/app/data")
GRPC_SERVICE2_PORT = os.environ.get("GRPC_SERVICE2_PORT", "50052")
GRPC_SERVICE2_HOST = os.environ.get("GRPC_SERVICE2_HOST", "localhost")
GRPC_SERVICE3_PORT = os.environ.get("GRPC_SERVICE3_PORT", "50053")
GRPC_SERVICE3_HOST = os.environ.get("GRPC_SERVICE3_HOST", "localhost")
# ------- --------------------- ---------

def read_images(folder_path):
    for image_name in os.listdir(folder_path):
        if image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(folder_path, image_name)
            with open(path, 'rb') as f:
                yield image_name, f.read()

def send_to_landmark(stub, filename, image_data):
    request = face_landmark_pb2.FaceImageRequest(filename=filename, image_data=image_data)
    stub.DetectLandmarks(request)

def send_to_age_gender(stub, filename, image_data):
    request = age_gender_pb2.AgeImageRequest(filename=filename, image_data=image_data)
    stub.Estimate(request)

def main():
    folder = DATA_DIR

    waittime = 10 
    print(f"wating for: {waittime} s")
    time.sleep(waittime)
    # gRPC channel to two services
    landmark_channel = grpc.insecure_channel(f'{GRPC_SERVICE2_HOST}:{GRPC_SERVICE2_PORT}')
    age_gender_channel = grpc.insecure_channel(f'{GRPC_SERVICE3_HOST}:{GRPC_SERVICE3_PORT}')

    landmark_stub = face_landmark_pb2_grpc.FaceLandmarkServiceStub(landmark_channel)
    age_gender_stub = age_gender_pb2_grpc.AgeGenderServiceStub(age_gender_channel)

    for filename, image_data in read_images(folder):
        print(f"Processing: {filename}")
        send_to_landmark(landmark_stub, filename, image_data)
        send_to_age_gender(age_gender_stub, filename, image_data)

if __name__ == "__main__":
    main()
