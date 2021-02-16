from redis_leader_election import LeaderElection
from redis import Redis
import datetime
import time

def elect_handler():
    print(datetime.datetime.now(), 'elected')

def error_handler(e):
    print(datetime.datetime.now(), e)

def revoke_handler():
    print(datetime.datetime.now(), 'revoked')

r = Redis(host='localhost', port=6379, db=0)

le = LeaderElection(r, lock_key='test')

le.on('elected', elect_handler)
le.on('error', error_handler)
le.on('revoked', revoke_handler)

le.elect()

while True:
    if le.is_leader():
        print(datetime.datetime.now(), 'doing the task')
        time.sleep(10)
        print(datetime.datetime.now(), 'done the task')
    time.sleep(50)