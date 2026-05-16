"""간단한 인메모리 LRU 캐시 — Free tier CPU 100초/일 절약 목적.

외부 의존성(redis 등) 없이 프로세스 메모리에서만 동작.
PythonAnywhere 무료티어는 1웹 워커 단일 프로세스라 캐시 일관성 문제 없음.
"""
from __future__ import annotations
from collections import OrderedDict
from functools import wraps
from threading import Lock
import time


class LRUCache:
    def __init__(self, max_size: int = 512, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._store: "OrderedDict[str, tuple[float, object]]" = OrderedDict()
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self._lock:
            v = self._store.get(key)
            if v is None:
                self.misses += 1
                return None
            ts, val = v
            if time.time() - ts > self.ttl:
                del self._store[key]
                self.misses += 1
                return None
            self._store.move_to_end(key)
            self.hits += 1
            return val

    def set(self, key, value):
        with self._lock:
            self._store[key] = (time.time(), value)
            self._store.move_to_end(key)
            while len(self._store) > self.max_size:
                self._store.popitem(last=False)


_caches = {}


def get_cache(name: str, max_size: int = 512, ttl: int = 3600) -> LRUCache:
    c = _caches.get(name)
    if c is None:
        c = LRUCache(max_size, ttl)
        _caches[name] = c
    return c


def cached(name: str, max_size: int = 512, ttl: int = 3600, key_fn=None):
    """함수 결과 캐싱 데코레이터."""
    cache = get_cache(name, max_size, ttl)

    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if key_fn:
                k = key_fn(*args, **kwargs)
            else:
                k = repr((args, tuple(sorted(kwargs.items()))))
            v = cache.get(k)
            if v is not None:
                return v
            v = fn(*args, **kwargs)
            cache.set(k, v)
            return v
        wrapper.cache = cache
        return wrapper
    return deco


def stats():
    return {
        name: {"size": len(c._store), "hits": c.hits, "misses": c.misses,
               "hit_rate": round(c.hits / (c.hits + c.misses) * 100, 1) if (c.hits + c.misses) else 0}
        for name, c in _caches.items()
    }
