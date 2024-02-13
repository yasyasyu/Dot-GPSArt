import math
import typing

import numpy as np


class AvailableException(Exception):
    def __init__(self, message="この地点・範囲では利用できません。"):
        super().__init__(message)


class InnerException(Exception):
    def __init__(self, message="ページを更新して、もう一度試してください。"):
        super().__init__(message)


def round_point(point: typing.Union[list, tuple], precision=7) -> tuple:
    return (round(point[0], precision), round(point[1], precision))


class UnionFind:
    """
    Implement (union by size) + (path compression)
    Reference:
    Zvi Galil and Giuseppe F. Italiano,
    Data structures and algorithms for disjoint set union problems
    """

    def __init__(self, n: int = 0):  # 初期化
        self._n = n
        self.parent_or_size = [-1] * n

    def merge(self, a: int, b: int) -> int:  # 結合
        assert 0 <= a < self._n
        assert 0 <= b < self._n

        x = self.leader(a)
        y = self.leader(b)

        if x == y:
            return x

        if -self.parent_or_size[x] < -self.parent_or_size[y]:
            x, y = y, x

        self.parent_or_size[x] += self.parent_or_size[y]
        self.parent_or_size[y] = x

        return x

    def same(self, a: int, b: int) -> bool:  # 判定
        assert 0 <= a < self._n
        assert 0 <= b < self._n

        return self.leader(a) == self.leader(b)

    def leader(self, a: int) -> int:  # 所属するグループのリーダー
        assert 0 <= a < self._n

        if self.parent_or_size[a] < 0:
            return a

        self.parent_or_size[a] = self.leader(self.parent_or_size[a])
        return self.parent_or_size[a]

    def size(self, a: int) -> int:  # 所属するグループのサイズ
        assert 0 <= a < self._n

        return -self.parent_or_size[self.leader(a)]

    def groups(self) -> typing.List[typing.List[int]]:  # グループを全表示
        leader_buf = [self.leader(i) for i in range(self._n)]

        result: typing.List[typing.List[int]] = [[] for _ in range(self._n)]
        for i in range(self._n):
            result[leader_buf[i]].append(i)

        return list(filter(lambda r: r, result))


def distance(A: typing.Union[list, tuple], B: typing.Union[list, tuple]) -> float:
    return math.sqrt((A[0] - B[0]) ** 2 + (A[1] - B[1]) ** 2)


def nearest_point(
    P: typing.Union[list, tuple],
    A: typing.Union[list, tuple],
    B: typing.Union[list, tuple],
) -> tuple:
    P = np.array(P)
    A = np.array(A)
    B = np.array(B)

    e = (B - A) / np.linalg.norm(B - A)

    return round_point(tuple(A + np.dot(P - A, e) * e))
