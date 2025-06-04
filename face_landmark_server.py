import grpc
from concurrent import futures
import time

# Import generated classes
from generated import face_landmark_pb2, face_landmark_pb2_grpc,aggregator_pb2,aggregator_pb2_grpc
from utils import compute_image_hash, save_to_redis, get_from_redis, is_complete, redis_client


class FaceLandmarkServiceServicer(face_landmark_pb2_grpc.FaceLandmarkServiceServicer):

    def __init__(self):
            channel = grpc.insecure_channel('localhost:50054')  # Aggregator
            self.aggregator_stub = aggregator_pb2_grpc.AggregatorStub(channel)
            
    def DetectLandmarks(self, request, context):
        image_hash = compute_image_hash(request.image_data)
        print(f"Processing face landmarks for {request.filename}, hash={image_hash}")

        landmarks_result = '{"points": [[1,2],[3,4]]}'  # Fake data
        save_to_redis(image_hash, 'landmarks', landmarks_result)

        if is_complete(image_hash):
            print("[Face_landmark_Server]:  Both age/gender and landmarks are ready. Sending to Aggregator.")
            self.aggregator_stub.SaveFaceAttributes(
                aggregator_pb2.FaceResult(
                    time=request.filename,
                    frame=request.image_data,
                    redis_key=image_hash
                )
            )
        return face_landmark_pb2.LandmarkResponse(success=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    face_landmark_pb2_grpc.add_FaceLandmarkServiceServicer_to_server(FaceLandmarkServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    print("Face Landmark Service running on port 50052...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()