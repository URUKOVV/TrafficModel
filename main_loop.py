import redis
import json
from bases import settings


redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
redis_instance.set('cars', json.dumps({'cars': [{'id': 1}]}))
print(redis_instance.get('cars'))
