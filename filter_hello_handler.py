import time
from pathlib import Path
import asyncio

    
async def filter_hello_handler(message):
    """filters messages for the keyword “hello” and prints the whole message to stdout"""
    if "hello" in message.split():
        print(message)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(filter_hello_handler("hello world"))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())  # see: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.shutdown_asyncgens
        loop.close()
