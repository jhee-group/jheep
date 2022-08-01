from typing import Protocol

from ..models import M_UUID, M


class FileObjectProtocol(Protocol[M]):
    model: Type[M]

    def __init__(
