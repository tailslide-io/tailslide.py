import asyncio

from flag_manager import FlagManager

app_id = 1
flag_name = 'Flag in app 1 number 1'

config = {
    "server": 'nats://localhost:4222',
    "app_id": 1,
    'user_context': '375d39e6-9c3f-4f58-80bd-e5960b710295',
    'sdk_key': 'myToken'
}




async def main():
    manager = FlagManager(**config)
    await manager.initialize_flags()
    
    flag_config = {
        "flag_name": flag_name
    }
    
    flag_toggler = manager.new_toggler(flag_config)
    
    while True:
        if (flag_toggler.is_flag_active()):
            print(f'Flag in {app_id} with name "{flag_name}" is active!')
        else:
            print(f'Flag in {app_id} with name "{flag_name}" is not active!')
            
        await asyncio.sleep(5)






if __name__ == '__main__':
    asyncio.run(main())
