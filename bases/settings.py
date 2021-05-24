import os

env = os.environ

REDIS_HOST = env.get('REDIS_HOST', 'localhost')
REDIS_PORT = env.get('REDIS_PORT', '6379')
