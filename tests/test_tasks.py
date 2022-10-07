from prefect import flow

from prefect_redis.tasks import (
    goodbye_prefect_redis,
    hello_prefect_redis,
)


def test_hello_prefect_redis():
    @flow
    def test_flow():
        return hello_prefect_redis()

    result = test_flow()
    assert result == "Hello, prefect-redis!"


def goodbye_hello_prefect_redis():
    @flow
    def test_flow():
        return goodbye_prefect_redis()

    result = test_flow()
    assert result == "Goodbye, prefect-redis!"
