import asyncio
from typing import List, Callable
from pathlib import Path

class Agent:
    def __init__(self, inbox_file_name: str, outbox_file_name: str):
        self.inbox_file_name = inbox_file_name
        self.outbox_file_name = outbox_file_name
        self.message_handlers: List[Callable] = []
        self.state_handlers: List[Callable] = []

    def register_message_handler(self, handler: Callable):
        self.message_handlers.append(handler)

    def register_state_handler(self, handler: Callable):
        self.state_handlers.append(handler)

    async def process_input(self, thefile):
        """Follow a file like tail -f."""
        thefile.seek(0,2)
        while True:
            line = thefile.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue
            yield line
            
    async def handle_outbox(self, message: str):
        """Handle writing messages to outbox file"""
        # Ensure the outbox file exists
        Path(self.outbox_file_name).touch(exist_ok=True)
        with open(self.outbox_file_name, 'a+') as f:
            f.write(message + '\n')
        
    async def handle_inbox(self):
        f = Path(self.inbox_file_name)
        f.touch(exist_ok=True)  # will create file, if it exists will do nothing
        try:
            with open(self.inbox_file_name, 'r') as f:
                async for line in self.process_input(f):
                    for handler in self.message_handlers:
                        await handler(line)
        except Exception as e:
            print(f"Error handling inbox: {e}")
    

    async def start(self):
        tasks = []
        # create task for reactive message handling
        task = asyncio.create_task(self.handle_inbox())
        tasks.append(task)
        # Create tasks for all handlers
        for handler in self.state_handlers:
            task = asyncio.create_task(
                handler(self.handle_outbox)
            )
            tasks.append(task)
        
        try:
            # Wait for all tasks to complete (they shouldn't complete normally)
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error in tasks: {e}")


if __name__ == '__main__':
    from generate_message_handler import generate_message_every_2_seconds
    agent = Agent(inbox_file_name="inbox.txt", outbox_file_name="outbox.txt")
    agent.register_state_handler(generate_message_every_2_seconds)
    asyncio.run(agent.start())
