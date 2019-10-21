from enum import Enum

import pytest

from django_ilmoitin.dummy_context import COMMON_CONTEXT, DummyContext
from django_ilmoitin.registry import notifications


def test_dummy_context_update_accepts_only_dicts():
    dummy_context = DummyContext()

    with pytest.raises(AssertionError):
        dummy_context.update("string")


def test_dummy_context_allows_only_registered_notification_types():
    dummy_context = DummyContext()

    with pytest.raises(AssertionError):
        dummy_context.update(
            {COMMON_CONTEXT: {"key": "value"}, "my_notification": {"key2": "value2"}}
        )


def test_dummy_context_allows_only_strings_as_keys_for_contexts():
    dummy_context = DummyContext()

    with pytest.raises(AssertionError):
        dummy_context.update(
            {COMMON_CONTEXT: {"key": "value"}, 777: {"key2": "value2"}}
        )


def test_dummy_context_builds_correctly():
    notifications.register("my_notification", "My notification")

    dummy_context = DummyContext()
    dummy_context.update(
        {COMMON_CONTEXT: {"key": "value"}, "my_notification": {"key2": "value2"}}
    )
    assert dummy_context.get("my_notification") == {"key": "value", "key2": "value2"}

    notifications.registry.clear()


def test_dummy_context_handles_enums():
    class MyEnum(Enum):
        FOO = "foo"

    notifications.register(MyEnum.FOO.value, "My enum foo")

    dummy_context = DummyContext()
    dummy_context.update(
        {COMMON_CONTEXT: {"key": "value"}, MyEnum.FOO: {"key2": "value2"}}
    )

    assert dummy_context.get(MyEnum.FOO) == {"key": "value", "key2": "value2"}

    notifications.registry.clear()
