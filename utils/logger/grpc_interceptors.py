import grpc
import time

from utils.logger.logging_config import logger

class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        handler = continuation(handler_call_details)
        if handler is None:
            return None

        if handler.unary_unary:
            def new_unary_unary(request, context):
                method = handler_call_details.method
                logger.info(f"[gRPC] Start method: {method}")
                start_time = time.time()
                try:
                    response = handler.unary_unary(request, context)
                    return response
                finally:
                    duration = (time.time() - start_time) * 1000
                    logger.info(f"[gRPC] End method: {method}, Duration: {duration:.2f} ms")

            return grpc.unary_unary_rpc_method_handler(
                new_unary_unary,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        # برای simplicity فقط unary_unary پیاده شده
        return handler
