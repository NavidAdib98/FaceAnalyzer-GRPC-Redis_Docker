import time
import grpc

def wait_for_grpc(host, port, timeout=10):
    channel = grpc.insecure_channel(f"{host}:{port}")
    start = time.time()
    while True:
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
            print(f"✅ gRPC server ready at {host}:{port}")
            return channel
        except grpc.FutureTimeoutError:
            if time.time() - start > timeout:
                raise TimeoutError(f"❌ gRPC server at {host}:{port} not available after {timeout} seconds.")
            print(f"⏳ Waiting for gRPC server at {host}:{port}...")
            time.sleep(1)