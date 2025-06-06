# aggregator_server.py

import grpc
from concurrent import futures
import time
import os
import json
import cv2
from datetime import datetime

from generated import aggregator_pb2, aggregator_pb2_grpc
from utils.utils import get_from_redis
from utils.face_utils import draw_combined_annotations
from utils.logger.grpc_interceptors import LoggingInterceptor


# ------- environment variables ---------
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', './output')
GRPC_SERVICE4_PORT = os.environ.get('GRPC_SERVICE4_PORT', '50054')
GRPC_SERVICE4_HOST = os.environ.get('GRPC_SERVICE4_HOST', "0.0.0.0") # for binding
# ------- --------------------- ---------


# Create output directory
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
    server.add_insecure_port(f"{GRPC_SERVICE4_HOST}:{GRPC_SERVICE4_PORT}")  # listening to port 50054 
    print(f"Starting Aggregator server on port {GRPC_SERVICE4_PORT}...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Stopping Aggregator server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
