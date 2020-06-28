from typing import Union

from .quest import QuestIE
from .servant import ServantIE


def extract_servant(html: Union[bytes, str]):
    return ServantIE(html).extract()


def extract_quest(html: Union[bytes, str]):
    return QuestIE(html).extract()


__all__ = ['extract_servant', 'extract_quest']
