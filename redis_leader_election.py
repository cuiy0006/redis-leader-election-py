import uuid
import hashlib
from threading import Timer
from redis import Redis, RedisError
from typing import Callable

class LeaderElection(object):
    def __init__(self, 
                 redis: Redis, 
                 lease_timeout: int=10000, 
                 acquire_lock_interval: int=1000,
                 lock_key: str='FillYourServiceName') -> None:

        self.id = str(uuid.uuid4())
        self.redis = redis
        self.lease_timeout = lease_timeout
        self.acquire_lock_interval = acquire_lock_interval

        sha = hashlib.sha1()
        sha.update(lock_key.encode())
        self.lock_key = sha.hexdigest()

        self.callbacks = {}

    def _renew(self):
        if self.is_leader():
            ok = -1
            try:
                ok = self.redis.pexpire(self.lock_key, self.lease_timeout)
            except RedisError as e:
                self._emit('error', e)

            if ok == 0:
                self._emit('error', KeyError('lock key does not exist when renew'))

            if ok != 1:
                if self.renew_timer:
                    self.renew_timer.cancel()
                self._emit('revoked')
                self.elect()
                
        else:
            if self.renew_timer:
                self.renew_timer.cancel()
            self._emit('revoked')
            self.elect()
            

    def elect(self):
        res = None
        try:
            res = self.redis.set(self.lock_key, self.id, px=self.lease_timeout, nx=True)
        except RedisError as e:
            self._emit('error', e)

        if res is None:
            self.elect_timer = Timer(self.acquire_lock_interval / 1000, self.elect)
            self.elect_timer.start()
        else:
            self._emit('elected')
            self.renew_timer = RepeatTimer(self.lease_timeout / 1000 / 2, self._renew)
            self.renew_timer.start()

    def is_leader(self) -> bool:
        id = None
        try:
            id = self.redis.get(self.lock_key)
        except RedisError as e:
            self._emit('error', e)

        id = id.decode()
        return (id is not None and id == self.id)

    def release(self):
        if self.is_leader():
            try:
                self.redis.delete(self.lock_key)
                self._emit('released')
            except RedisError as e:
                self._emit('error', e)
        if self.renew_timer:
            self.renew_timer.cancel()
        if self.elect_timer:
            self.elect_timer.cancel()

    def on(self, event_name: str, callback: Callable):
        if event_name not in self.callbacks:
            self.callbacks[event_name] = [callback]
        else:
            self.callbacks[event_name].append(callback)

    def _emit(self, event_name: str, *args):
        if event_name not in self.callbacks:
            return
        for callback in self.callbacks[event_name]:
            callback(*args)

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
