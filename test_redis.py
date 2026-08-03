from services.redis import redis_client

redis_client.set("test", "hello")

value = redis_client.get("test")

print(value)