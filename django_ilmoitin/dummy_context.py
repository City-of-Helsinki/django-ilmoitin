from collections import defaultdict
from copy import deepcopy
from enum import Enum
from typing import Any, Mapping, Type, Union

from .registry import notifications

_StrOrEnum = Union[str, Type[Enum]]

COMMON_CONTEXT = "__common__"


class DummyContext:
    context = defaultdict(dict)

    def update(self, context_dict: Mapping[_StrOrEnum, Mapping[str, Any]]) -> None:
        """
        Proxy helper method that makes updating
        DummyContext's context storage less verbose.

        :param context_dict: dictionary of values to be put into dummy context
        """
        assert isinstance(
            context_dict, Mapping
        ), "DummyContext's update() method accepts only dictionaries."

        for type_code, context in context_dict.items():
            if isinstance(type_code, Enum):
                type_code = type_code.value

            self._assert_type_code_is_str(type_code)
            if not type_code == COMMON_CONTEXT:
                self._assert_notification_type_exists(type_code)

            self.context.update({type_code: context})

    def get(self, type_code: _StrOrEnum) -> dict:
        """
        Proxy helper method that makes fetching from
        DummyContext's context storage less verbose.

        :param type_code: code of the notification type
        :return: dummy context for the notification type
        """
        if isinstance(type_code, Enum):
            type_code = type_code.value

        self._assert_type_code_is_str(type_code)
        self._assert_notification_type_exists(type_code)

        context = deepcopy(self.context.get(COMMON_CONTEXT)) or {}
        context.update(self.context.get(type_code, {}))
        return context

    @staticmethod
    def _assert_type_code_is_str(type_code: str) -> None:
        assert isinstance(type_code, str), (
            "Expected a string code for a notification"
            "template's type, received {}".format(type(type_code))
        )

    @staticmethod
    def _assert_notification_type_exists(type_code: str) -> None:
        assert type_code in notifications.registry, (
            "This type of notification is not"
            "registered with the ilmoitin: {}".format(type_code)
        )


dummy_context = DummyContext()
