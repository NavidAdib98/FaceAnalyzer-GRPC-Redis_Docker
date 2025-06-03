import grpc
from concurrent import futures
import time

# Import generated classes
from generated import face_landmark_pb2, face_landmark_pb2_grpc


class FaceLandmarkServiceServicer(face_landmark_pb2_grpc.FaceLandmarkServiceServicer):

    def DetectLandmarks(self, request, context):
        print(f"Received request for file: {request.filename}")
        # فقط یک پاسخ ساده می‌دهیم
        print("image is in progress with face datection")
        return face_landmark_pb2.LandmarkResponse(success=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    face_landmark_pb2_grpc.add_FaceLandmarkServiceServicer_to_server(FaceLandmarkServiceServicer(), server)
    server.add_insecure_port('[::]:50052')  # listening on port 50052
    print("Starting FaceLandmarkService server on port 50052...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # 1 day sleep 
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop(0)

if __name__ == '__main__':
    serve()