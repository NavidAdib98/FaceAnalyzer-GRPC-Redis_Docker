import grpc
from concurrent import futures
import time

# Import generated classes
from generated import age_gender_pb2, age_gender_pb2_grpc


class AgeGenderServiceServicer(age_gender_pb2_grpc.AgeGenderServiceServicer):

    def Estimate(self, request, context):
        print(f"Received request for file: {request.filename}")
        print("image is in progress with age/gender prediction")

        # فقط یک پاسخ تستی بازمی‌گردانیم
        return age_gender_pb2.AgeGenderResponse(estimated_age=25, gender="Male", success=True)


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
