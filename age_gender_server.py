import grpc
import json
from concurrent import futures
import time

# Import generated classes
from generated import age_gender_pb2, age_gender_pb2_grpc,aggregator_pb2, aggregator_pb2_grpc
from utils.utils import compute_image_hash, save_to_redis, get_from_redis, is_complete, redis_client



class AgeGenderServiceServicer(age_gender_pb2_grpc.AgeGenderServiceServicer):

    def __init__(self):
        channel = grpc.insecure_channel('localhost:50054')  # Aggregator
        self.aggregator_stub = aggregator_pb2_grpc.AggregatorStub(channel)

    def Estimate(self, request, context):
        image_hash = compute_image_hash(request.image_data)
        print(f"Processing age/gender for {request.filename}, hash={image_hash}")

        result = json.dumps({"age": 25, "gender": "male"})  # Fake data
        save_to_redis(image_hash, 'age_gender', result)

        if is_complete(image_hash):
            print("[Age_Gender_Server]:  Both landmarks and age/gender available. Sending to Aggregator.")
            self.aggregator_stub.SaveFaceAttributes(
                aggregator_pb2.FaceResult(
                    time=request.filename,
                    frame=request.image_data,
                    redis_key=image_hash
                )
            )

        return age_gender_pb2.AgeGenderResponse(estimated_age=25, gender="male", success=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    age_gender_pb2_grpc.add_AgeGenderServiceServicer_to_server(AgeGenderServiceServicer(), server)
    server.add_insecure_port('[::]:50053')  # listening on port 50053
    print("Starting AgeGenderService server on port 50053...")
    server.start()
    try:
        while True:
            time.sleep(86400)  # 1 day sleep
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
