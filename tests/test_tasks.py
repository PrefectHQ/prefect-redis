"""Test Redis tasks"""
import string
import os
import random
from typing import Dict

import pytest

from prefect_redis import (
    RedisCredentials, redis_set, redis_set_binary, redis_get, redis_get_binary, redis_execute,
)


@pytest.fixture
def environ_credentials() -> Dict:
    return {
        "host": os.environ["TEST_REDIS_HOST"],
        "port": os.environ["TEST_REDIS_PORT"],
        "db": os.environ.get("TEST_REDIS_DB", "0"),
        "username": os.environ["TEST_REDIS_USERNAME"],
        "password": os.environ["TEST_REDIS_PASSWORD"]
    }


@pytest.fixture
def redis_credentials(environ_credentials: Dict) -> RedisCredentials:
    return RedisCredentials(**environ_credentials)


@pytest.fixture
def random_key() -> str:
    return "".join(random.sample(string.ascii_lowercase, 10))


@pytest.mark.asyncio
async def test_from_credentials(redis_credentials: RedisCredentials):
    """Test instantiating credentials"""
    client = redis_credentials.get_client()
    await client.ping()

    await client.close()


@pytest.mark.asyncio
async def test_from_connection_string(environ_credentials: Dict):

    connection_string = "redis://{username}:{password}@{host}:{port}/{db}".format(**environ_credentials)
    redis_credentials = RedisCredentials.from_connection_string(connection_string)

    client = redis_credentials.get_client()
    await client.ping()

    await client.close()


@pytest.mark.asyncio
async def test_set_get_bytes(redis_credentials: RedisCredentials, random_key: str):

    ref_string = b"hello world"

    await redis_set_binary.fn(redis_credentials, random_key, ref_string, ex=60)
    test_value = await redis_get_binary.fn(redis_credentials, random_key)

    assert test_value == ref_string


async def test_set_get(redis_credentials: RedisCredentials, random_key: str):

    ref_string = "hello world"

    await redis_set.fn(redis_credentials, random_key, ref_string, ex=60)
    test_value = await redis_get.fn(redis_credentials, random_key)

    assert test_value == ref_string


async def test_set_obj(redis_credentials: RedisCredentials, random_key: str):

    ref_obj = ("foobar", 123, {"hello": "world"})

    await redis_set.fn(redis_credentials, random_key, ref_obj, ex=60)
    test_value = await redis_get.fn(redis_credentials, random_key)

    assert type(ref_obj) == type(test_value)
    assert len(ref_obj) == len(test_value)

    assert ref_obj[0] == test_value[0]
    assert ref_obj[1] == test_value[1]

    ref_dct = ref_obj[2]
    test_dct = test_value[2]

    for ref_key, test_key in zip(ref_dct, test_dct):
        assert ref_key == test_key
        assert ref_dct[ref_key] == test_dct[test_key]


async def test_execute(redis_credentials: RedisCredentials):

    await redis_execute.fn(redis_credentials, "ping")
