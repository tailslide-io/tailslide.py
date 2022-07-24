import redis


class RedisTimeSeriesClient:
  def __init__(self, redis_host, redis_port):
    self.redis_host = redis_host or 'localhost'
    self.redis_port = redis_port or 6379
    self.redis_client = None
  
  def init(self):
    self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port)
  
  def emit_signal(self, flag_id, app_id, status):
    self.redis_client.ts().add(f'{flag_id}:{status}', '*', 1,
                               labels={"status":status, "flagId": flag_id, "appId": app_id})
  
  def disconnect(self):
    self.redis_client.quit()

    
    
    
  
