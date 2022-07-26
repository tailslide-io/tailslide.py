import asyncio
import random

from flag_manager import FlagManager

app_id = 1
stream = 'flags_ruleset'
flag_name = 'App 1 Flag 1'

config = {
    "nats_server": 'localhost:4222',
    "stream": stream,
    "app_id": 1,
    'user_context': '375d39e6-9c3f-4f58-80bd-e5960b710295',
    'sdk_key': 'myToken',
    'redis_host': 'localhost',
    'redis_port': 6379
}




async def main():
    manager = FlagManager(**config)
    await manager.initialize_flags()
    
    flag_config = {
        "flag_name": flag_name
    }
    
    flag_toggler = manager.new_toggler(flag_config)
    
    if (flag_toggler.is_flag_active()):
        print(f'Flag in {app_id} with name "{flag_name}" is active!')
        flag_toggler.emit_success()
    else:
        print(f'Flag in {app_id} with name "{flag_name}" is not active!')
        flag_toggler.emit_failure()

    count = 1
    limit = 50 
    while count < limit:
        random_int = random.random()
        
        if random_int < 1:
            print("Emitting success")
            flag_toggler.emit_success()
        else:
            print("Emitting failure")
            flag_toggler.emit_failure()
            
        await asyncio.sleep(0.5)
        count+= 1

    await manager.disconnet()
    print("cliencts disconnected")
    



if __name__ == '__main__':
    asyncio.run(main())
