import random
import time
from typing import Callable
import asyncio

WORDS_SOUP = ["hello", "sun", "world", "space", "moon", "crypto", "sky", "ocean", "universe", "human"]


async def generate_message_every_2_seconds(handle_message: Callable):
    while True:
        word1 = random.choice(WORDS_SOUP)
        word2 = random.choice(WORDS_SOUP)
        message = " ".join([word1, word2])
        await handle_message(message)
        await asyncio.sleep(2)

if __name__ == '__main__':
    async def handle_message(message):
        print(message)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(generate_message_every_2_seconds(handle_message))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())  # see: https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.shutdown_asyncgens
        loop.close()
