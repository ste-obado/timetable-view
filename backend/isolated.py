from redis_client import redis_client

redis_client.set("test_key", "hello redis")
print(redis_client.get("test_key"))