## Set up env  
```
python3 -m venv env
. env/bin/activate
pip3 install redis
```
<br/><br/>
## API
```
r = Redis(host='localhost', port=6379, db=0)
le = LeaderElection(r, lease_timeout=10000, acquire_lock_interval=1000, lock_key='test')
```
Initialize a leader election  
`lease_timeout` is lease period for a leader  
`acquire_lock_interval` is the interval between the actions to try to be elected as a leader  
`lock_key` is a unique key for a leader election containing competing services
<br/><br/>

```
le.on('elected', elect_handler)
le.on('error', error_handler)
le.on('released', release_handler)
```
Subscribe events of leader election  
<br/><br/>
  
```
le.elect()
```
Start to join the election  
<br/><br/>
  
```
le.is_leader()
```
Return whether the service the leader now  
<br/><br/>
  
```
le.release()
```
Exit from the leader election  
