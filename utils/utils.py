# utils.py
import hashlib
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

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
