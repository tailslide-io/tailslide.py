import redis

flag_id = 1
app_id = 1
status= 'success'

redisClient = redis.Redis(host='localhost', port=6379)
redisClient.ts().add(f'{flag_id}:{status}', '*',1, labels={"status":status, "flagId": flag_id, "appId": app_id})
