# aggregator_server.py

import grpc
from concurrent import futures
import time
from generated import aggregator_pb2, aggregator_pb2_grpc


class AggregatorServicer(aggregator_pb2_grpc.AggregatorServicer):

    def SaveFaceAttributes(self, request, context):
        print(f"[{request.time}] Received frame with redis_key: {request.redis_key}")
        
        return aggregator_pb2.FaceResultResponse(response=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    aggregator_pb2_grpc.add_AggregatorServicer_to_server(AggregatorServicer(), server)
    server.add_insecure_port('[::]:50054')  # listening to port 50054 
    print("Starting Aggregator server on port 50054...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Stopping Aggregator server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
