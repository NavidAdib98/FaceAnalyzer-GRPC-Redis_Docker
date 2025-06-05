# utils.py
import hashlib
import redis
import json

# ------- config.yaml ---------
from config_loader import config
config_redis_port = config['redis']['port']
config_redis_host = config['redis']['host']
config_redis_db = config['redis']['db']
# ------- ------------ ---------

redis_client = redis.Redis(host=config_redis_host, port=config_redis_port, db=config_redis_db)

def compute_image_hash(image_data: bytes) -> str:
    return hashlib.sha256(image_data).hexdigest()

def save_to_redis(key: str, field: str, value):
    current = redis_client.hgetall(key)
    current_data = {k.decode(): v.decode() for k, v in current.items()}
    current_data[field] = value
    redis_client.hmset(key, current_data)

def get_from_redis(key: str):
    raw = redis_client.hgetall(key)
    return {k.decode(): v.decode() for k, v in raw.items()}

def is_complete(key: str):
    data = get_from_redis(key)
    return 'landmarks' in data and 'age_gender' in data
