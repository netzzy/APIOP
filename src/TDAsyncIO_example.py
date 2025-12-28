import asyncio

async def test():
    await asyncio.sleep(3)
    print('hello world')
    
# Run coroutine
coroutines = [test()]
op("TDAsyncIO").Run(coroutines)


