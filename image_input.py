import os, sys
import grpc
from pathlib import Path

from generated import face_landmark_pb2
from generated import age_gender_pb2
from generated import age_gender_pb2_grpc
from generated import face_landmark_pb2_grpc

# ------- config.yaml ---------
from config_loader import config
config_grpc2_port = config['grpc']["service2"]['port']
config_grpc3_port = config['grpc']["service3"]['port']
config_grpc4_port = config['grpc']["service4"]['port']
# ------- ------------ ---------



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
    folder = "/Users/adib/Desktop/task/task/data"

    # gRPC channel to two services
    landmark_channel = grpc.insecure_channel(f'localhost:{config_grpc2_port}')
    age_gender_channel = grpc.insecure_channel(f'localhost:{config_grpc3_port}')

    landmark_stub = face_landmark_pb2_grpc.FaceLandmarkServiceStub(landmark_channel)
    age_gender_stub = age_gender_pb2_grpc.AgeGenderServiceStub(age_gender_channel)

    for filename, image_data in read_images(folder):
        print(f"Processing: {filename}")
        send_to_landmark(landmark_stub, filename, image_data)
        send_to_age_gender(age_gender_stub, filename, image_data)

if __name__ == "__main__":
    main()
