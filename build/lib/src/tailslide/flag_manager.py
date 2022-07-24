from nats_client import NatsClient
from toggler import Toggler


class FlagManager:
  def __init__(self, server='', app_id='', sdk_key='', user_context='', redis_address=''):
    self.nats_client = NatsClient(server=server, subject=app_id, callback=self._set_flags, sdk_key=sdk_key)
    # self.redis_ts_client = RedisTimeSeriesClient(redis_address)
    
    self.flags = []
    self.user_context = user_context
    
  async def initialize_flags(self):
    await self.nats_client.initialize_flags()
    # await self.redis_ts_client.init()
    
  
  def _set_flags(self, flags):
    self.flags= flags
  
  def get_flags(self):
    return self.flags
    
  async def disconnet(self):
    await self.nats_client.disconnect()
    # await self.redis_ts_client.disconnect()

  def new_toggler(self,config):
    new_toggle = Toggler(**config, get_flags=self.get_flags, user_context=self.user_context)
    return new_toggle
  



