from __future__ import annotations

from collections import deque


class InMemoryMessageQueue:
    def __init__(self, maxlen: int = 1000):
        self._queue = deque(maxlen=maxlen)

    def put(self, message) -> None:
        if len(self._queue) == self._queue.maxlen:
            raise OverflowError('message queue is full')
        self._queue.append(message)

    def get(self):
        if not self._queue:
            return None
        return self._queue.popleft()

    def __len__(self) -> int:
        return len(self._queue)
