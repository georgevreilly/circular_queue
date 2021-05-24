#!/usr/bin/env python3

import random


class QueueFullError(Exception):
    """queue full"""


class QueueEmptyError(Exception):
    """queue empty"""


class BaseCircularQueue:
    def __init__(self, size):
        self.size = size  # aka capacity
        self.data = [None] * size
        self.read = self._initial_index()  # aka head
        self.write = self._initial_index()  # aka tail
        assert self.is_empty()

    def push(self, value):
        if self.is_full():
            raise QueueFullError()
        self.data[self._index(self.write)] = value
        self.write = self._next_index(self.write)
        assert self._count() > 0
        assert not self.is_empty()

    def pull(self):
        if self.is_empty():
            raise QueueEmptyError()
        assert self._count() > 0
        index = self._index(self.read)
        value, self.data[index] = self.data[index], None
        self.read = self._next_index(self.read)
        assert not self.is_full()
        return value

    enqueue = push
    dequeue = pull

    def peek(self):
        if self.is_empty():
            return None
        return self.data[self._index(self.read)]

    def is_empty(self):
        # return len(self) == 0
        v = self._is_empty()
        assert v == (self._count() == 0), f"{v}, {self._count()}"
        return v

    def is_full(self):
        # return len(self) == self._max_capacity()
        v = self._is_full()
        assert v == (self._count() == self._max_capacity()), f"{v}, {self._count()}"
        return v

    def __len__(self):
        v = self._count()
        empty_slots = self.data.count(None)
        assert v == self.size - empty_slots, f"{v} != {self.size} - {empty_slots}"
        return v
    
    def __repr__(self):
        return "<{}({}) write={} read={} len={} data={!r}>".format(
                self.__class__.__name__, self.size,
                self.write, self.read,
                len(self), self.data)

    def _max_capacity(self):
        return self.size

    def _initial_index(self):
        return 0

    def _index(self, index):
        return index % self.size

    def _next_index(self, index):
        return (index + 1) % self.size

    def _is_empty(self):
        raise NotImplementedError()

    def _is_full(self):
        raise NotImplementedError()

    def _count(self):
        raise NotImplementedError()


class CircularQueue(BaseCircularQueue):
    def _index(self, index):
        # return index % self.size
        assert 0 <= index < 2 * self.size
        index2 = index - self.size
        if index2 >= 0:
            index = index2
        assert 0 <= index < self.size
        return index

    def _next_index(self, index):
        # return (index + 1) % (2 * self.size)
        assert 0 <= index < 2 * self.size
        index += 1
        if index == self.size + self.size:
            index = 0
        assert 0 <= index < 2 * self.size
        return index

    def _is_empty(self):
        return self.write == self.read

    def _is_full(self):
        c = self.write - self.read
        c = (-c if c < 0 else c)
        # write and read are diametrically opposed on the double ring when full
        return c == self.size

    def _count(self):
        c = self.write - self.read
        if c >= 0:
            return c
        else:
            return c + self.size + self.size


class BackwardCircularQueue(CircularQueue):
    def _initial_index(self):
        return 2 * self.size - 1

    def _next_index(self, index):
        assert 0 <= index < 2 * self.size
        if index == 0:
            index = self.size + self.size
        index -= 1
        assert 0 <= index < 2 * self.size
        return index

    def _count(self):
        # Because counting down, read >= write, usually
        c = self.read - self.write
        if c >= 0:
            return c
        else:
            return c + self.size + self.size


class UnfilledCircularQueue(BaseCircularQueue):
    def _max_capacity(self):
        return self.size - 1

    def _index(self, index):
        return index

    def _next_index(self, index):
        return (index + 1) % self.size

    def _is_empty(self):
        return self.write == self.read

    def _is_full(self):
        return self.read == (self.write + 1) % self.size

    def _count(self):
        if self.write >= self.read:
            return self.write - self.read
        else:
            return self.size + self.write - self.read


class NegativeCircularQueue(BaseCircularQueue):
    Empty = -1

    def push(self, value):
        if self.is_full():
            raise QueueFullError()
        if self.is_empty():
            self.write = self.read = 0
            assert self._count() == 1
        else:
            self.write = self._next_index(self.write)
            assert self._count() > 1
        self.data[self.write] = value
        assert not self.is_empty()

    def pull(self):
        if self.is_empty():
            raise QueueEmptyError()
        value, self.data[self.read] = self.data[self.read], None
        if self.read == self.write:
            assert self._count() == 1
            self.read = self.write = self.Empty
            assert self.is_empty()
        else:
            assert self._count() > 1
            self.read = self._next_index(self.read)
            assert not self.is_empty()
        assert not self.is_full()
        return value

    def _initial_index(self):
        return self.Empty

    def _next_index(self, index):
        assert 0 <= index < self.size
        index = (index + 1) % self.size
        assert 0 <= index < self.size
        return index

    def _is_empty(self):
        self._is_valid_read_write()
        return self.read == self.Empty

    def _is_full(self):
        self._is_valid_read_write()
        return self.write != self.Empty and self._next_index(self.write) == self.read

    def _count(self):
        self._is_valid_read_write()
        if self.read == self.Empty:
            return 0
        return 1 + (self.size + self.write - self.read) % self.size

    def _is_valid_read_write(self):
        if self.read == self.Empty:
            assert self.write == self.Empty
        else:
            assert self.write != self.Empty
            assert 0 <= self.read < self.size
            assert 0 <= self.write < self.size


class BackwardNegativeCircularQueue(NegativeCircularQueue):
    def _next_index(self, index):
        assert 0 <= index < self.size
        if index == 0:
            index = self.size
        index -= 1
        assert 0 <= index < self.size
        return index

    def _count(self):
        self._is_valid_read_write()
        if self.read == self.Empty:
            return 0
        return 1 + (self.size + self.read - self.write) % self.size


def exercise_circular_queue(queue_class, size, item_count):
    items = iter(range(1, item_count+1))
    cq = queue_class(size)
    results = []
    print(cq)
    for i in range(random.randint(0, 3 * size // 4)):
        value = next(items)
        cq.push(value)
        print("w", value, cq)
    more = True

    while more:
        if random.randint(0, 1) == 0:
            # push
            if cq.is_full():
                print("F", cq)
            else:
                value = next(items, None)
                if value is None:
                    more = False
                    print("<NoMore>")
                else:
                    cq.push(value)
                    print("W", value, cq)
        else:
            # pull
            if cq.is_empty():
                print("\tE", cq)
            else:
                peek = cq.peek()
                value = cq.pull()
                assert peek == value
                results.append(value)
                print("\tR", value, cq)
    while not cq.is_empty():
        value = cq.pull()
        results.append(value)
        print("\tr", value, cq)
    print(cq)
    print(results)
    assert len(results) == item_count, f"{len(results)}, {item_count}"
    assert results == list(range(1, item_count+1))


if __name__ == '__main__':
    classes = (
        NegativeCircularQueue,
        BackwardNegativeCircularQueue,
        UnfilledCircularQueue,
        CircularQueue,
        BackwardCircularQueue,
    )
    for queue_class in classes:
        print(f"\n\n=== {queue_class.__name__} ===\n")
        exercise_circular_queue(queue_class, 4, 100)
