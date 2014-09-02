from injector import inject, Module, provides, singleton

from smarkets.interfaces import Redis, RedisConfiguration


class RedisModule(Module):

    def __init__(self, strict_client=True):
        import redis
        self.client_class = redis.StrictRedis if strict_client else redis.Redis

    @singleton
    @provides(Redis)
    @inject(c=RedisConfiguration)
    def provide_redis(self, c):
        return self.client_class(**c._asdict())
