import grpc
import json
from concurrent import futures
import time

# Import generated classes
from generated import age_gender_pb2, age_gender_pb2_grpc,aggregator_pb2, aggregator_pb2_grpc

# import utils
from utils.utils import compute_image_hash, save_to_redis, is_complete, redis_client
from utils.face_utils import detect_faces,predict_age_gender_with_padding
from utils.logger.grpc_interceptors import LoggingInterceptor




# ------- config.yaml ---------
from config_loader import config
config_grpc3_port = config['grpc']["service3"]['port']
config_grpc4_port = config['grpc']["service4"]['port']
config_grpc3_host = config['grpc']["service3"]['host']
config_grpc4_host = config['grpc']["service4"]['host']
config_output_dir = config["output"]["dir"]
# ------- ------------ ---------


class AgeGenderServiceServicer(age_gender_pb2_grpc.AgeGenderServiceServicer):

    def __init__(self):
        channel = grpc.insecure_channel(f'{config_grpc4_host}:{config_grpc4_port}')  # Aggregator
        self.aggregator_stub = aggregator_pb2_grpc.AggregatorStub(channel)

    def Estimate(self, request, context):
        image_hash = compute_image_hash(request.image_data)
        print(f"Processing age/gender for {request.filename}, hash={image_hash}")

        # face detection:
        faces, gray_frame, color_image = detect_faces(request.image_data)
        if not faces:
            print("[Age_Gender_Server]: No face detected.")
            return age_gender_pb2.AgeGenderResponse(
                success=False,
                faces=[]
            )
        # age-gender predicion
        predictions = predict_age_gender_with_padding(color_image, faces)
        if not predictions:
            print("[Age_Gender_Server]: Prediction failed.")
            return age_gender_pb2.AgeGenderResponse(
                success=False,
                faces=[]
            )
        # make resualt ready for sending
        faces_response = []
        redis_result = []

        for pred in predictions:
            age_string = pred["age"]      # مثلاً "25-32"
            gender = pred["gender"]       # "Male" یا "Female"
            x1, y1, x2, y2 = pred["box"]

            # اضافه کردن به پاسخ gRPC
            face_attr = age_gender_pb2.FaceAttributes(
                estimated_age=age_string,
                gender=gender.lower(),
                box=age_gender_pb2.BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2)
            )
            faces_response.append(face_attr)

            # آماده‌سازی برای ذخیره‌سازی در Redis
            redis_result.append({
                "age": age_string,
                "gender": gender,
                "box": [x1, y1, x2, y2]
            })

        # ذخیره در Redis
        save_to_redis(image_hash, 'age_gender', json.dumps(redis_result))

        if is_complete(image_hash):
            print("[Age_Gender_Server]:  Both landmarks and age/gender available. Sending to Aggregator.")
            self.aggregator_stub.SaveFaceAttributes(
                aggregator_pb2.FaceResult(
                    time=request.filename,
                    frame=request.image_data,
                    redis_key=image_hash
                )
            )

        return age_gender_pb2.AgeGenderResponse(
            success=True,
            faces=faces_response
)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=[LoggingInterceptor()]
                         )
    age_gender_pb2_grpc.add_AgeGenderServiceServicer_to_server(AgeGenderServiceServicer(), server)
    server.add_insecure_port(f"{config_grpc3_host}:{config_grpc3_port}")  # listening to port 50053
    print(f'Starting AgeGenderService server on port {config_grpc3_port}...')
    server.start()
    try:
        while True:
            time.sleep(86400)  # 1 day sleep
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
