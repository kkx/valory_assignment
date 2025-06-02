import asyncio

from agent import Agent
from generate_message_handler import generate_message_every_2_seconds
from filter_hello_handler import filter_hello_handler

if __name__ == '__main__':
    agent2 = Agent(inbox_file_name="outbox.txt", outbox_file_name="inbox.txt")
    agent2.register_state_handler(generate_message_every_2_seconds)
    agent2.register_message_handler(filter_hello_handler)
    try:
        asyncio.run(agent2.start())
    except KeyboardInterrupt:
        print("\nStopping agent...")


