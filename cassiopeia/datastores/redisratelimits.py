from time import sleep

from merakicommons.ratelimits import RateLimiter

from redis import ConnectionPool
from redis_rate_limit import RateLimit, TooManyRequests


class RedisFixedWindowRateLimiter(RateLimiter):
    def __init__(self, window_seconds: int, window_permits: int, store_key: str, redis: dict) -> None:
        self._window_seconds = window_seconds
        self._window_permits = window_permits
        self._store_key = store_key
        self._host = redis['host']
        self._port = redis['port']
        self._db = redis['db']

        if 'password' in redis:
            self._password = redis['password']
            self._redis_pool = ConnectionPool(host=self._host, port=self._port, db=self._db, password=self._password)
        else:
            self._redis_pool = ConnectionPool(host=self._host, port=self._port, db=self._db)

        # print(
        #     f'{self._store_key}: init with {self._window_permits} per {self._window_seconds}s on {self._host}:'
        #     f'{self._port}')

        self._permitter = RateLimit(resource=self._store_key, client=self._host, max_requests=self._window_permits,
                                    redis_pool=self._redis_pool)

    def __enter__(self) -> "RedisFixedWindowRateLimiter":
        # print(f'{self._store_key}: __enter__')
        while True:
            try:
                # print(f'{self._store_key}: current usage: {self._permitter.get_usage()}')
                with self._permitter:
                    # print(f'{self._store_key}: acquired!')
                    return self
            except TooManyRequests:
                sl = self._permitter.get_wait_time()
                # print(f'{self._store_key}: sleeping {sl}')
                sleep(sl)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # print(f'{self._store_key}: __exit__')
        pass

    def set_permits(self, permits: int) -> None:
        # print(f'{self._store_key}: __exit__')
        pass

    @property
    def permits_issued(self) -> int:
        # print(f'{self._store_key}: permits_issued')
        pass

    def reset_permits_issued(self) -> None:
        # print(f'{self._store_key}: reset_permits_issued')
        pass
