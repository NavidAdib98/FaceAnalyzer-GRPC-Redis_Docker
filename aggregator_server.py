# aggregator_server.py

import grpc
from concurrent import futures
import time
import os
import json
from datetime import datetime
import redis
import cv2


from generated import aggregator_pb2, aggregator_pb2_grpc
from utils.utils import get_from_redis
from utils.face_utils import draw_combined_annotations
from utils.logger.grpc_interceptors import LoggingInterceptor

# ------- config.yaml ---------
from config_loader import config
service_name = "service4"
config_grpc_host = config['grpc'][service_name]['host']
config_grpc_port = config['grpc'][service_name]['port']
config_output_dir = config["output"]["dir"]
# ------- ------------ ---------


# Create output directory
OUTPUT_DIR = config_output_dir
os.makedirs(OUTPUT_DIR, exist_ok=True)


class AggregatorServicer(aggregator_pb2_grpc.AggregatorServicer):

    def SaveFaceAttributes(self, request, context):
        redis_key = request.redis_key
        image_data = request.frame
        redis_time = request.time

        # Retrieve data from Redis
        data = get_from_redis(redis_key)
        if not data:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"No data found in Redis for key: {redis_key}")
            return aggregator_pb2.FaceResultResponse(response=False)

        # Generate filename
        safe_time = redis_time.replace(":", "_").replace("/", "_") if redis_time else datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{safe_time}_{redis_key}"

        # draw landmarks and (age-gender) annotation on image before saving
        # print(data)
        data['landmarks'] = json.loads(data['landmarks'])
        data['age_gender'] = json.loads(data['age_gender'])
        final_image = draw_combined_annotations(image_data, data)
        
        # Save image
        image_path = os.path.join(OUTPUT_DIR, base_filename + ".jpg")
        cv2.imwrite(image_path, final_image)

        # Save JSON
        json_path = os.path.join(OUTPUT_DIR, base_filename + ".json")
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)


        print(f"Saved image and data for {redis_key} at {safe_time}")
        return aggregator_pb2.FaceResultResponse(response=True)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=[LoggingInterceptor()]
                         )
    aggregator_pb2_grpc.add_AggregatorServicer_to_server(AggregatorServicer(), server)
    server.add_insecure_port(f"[::]:{config_grpc_port}")  # listening to port 50054 
    print(f"Starting Aggregator server on port {config_grpc_port}...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Stopping Aggregator server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
