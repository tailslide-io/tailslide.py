from .nats_client import NatsClient
from .redis_timeseries_client import RedisTimeSeriesClient
from .toggler import Toggler


class FlagManager:
  def __init__(self, nats_server='localhost:4222', nats_stream='flags_ruleset', app_id='', sdk_key='', user_context='', redis_host='localhost', redis_port=6379):
    self._nats_client = NatsClient(server=nats_server, stream=nats_stream, subject=app_id, callback=self.set_flags, token=sdk_key)
    self._redis_ts_client = RedisTimeSeriesClient(redis_host, redis_port)
    
    self._flags = []
    self._user_context = user_context
    
  async def initialize_flags(self):
    await self._nats_client.initialize_flags()
    self._redis_ts_client.init()
    
  
  def set_flags(self, flags):
    self._flags= flags
  
  def get_flags(self):
    return self._flags

  def set_user_context(self, new_user_context):
    self._user_context = new_user_context
  
  def get_user_context(self):
    return self._user_context
    
  async def disconnet(self):
    await self._nats_client.disconnect()
    self._redis_ts_client.disconnect()

  def new_toggler(self,config):
    return Toggler(**config, get_flags=self.get_flags, user_context=self._user_context,
                        emit_redis_signal=self._redis_ts_client.emit_signal
                   )
  



