import asyncio
import os
from pathlib import Path
import unittest
from unittest import IsolatedAsyncioTestCase
from agent import Agent
from generate_message_handler import generate_message_every_2_seconds
from filter_hello_handler import filter_hello_handler

class TestTwoAgentIntegration(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Setup file paths
        self.agent1_inbox = "agent1_inbox.txt"
        self.agent1_outbox = "agent1_outbox.txt"  # This will be agent2's inbox
        self.agent2_inbox = self.agent1_outbox     # Connect the files
        self.agent2_outbox = self.agent1_inbox  # This will be agent1's inbox
        
        # Clean up any existing files
        for file in [self.agent1_inbox, self.agent1_outbox]:
            if os.path.exists(file):
                os.remove(file)
        
        # Create agents
        self.agent1 = Agent(self.agent1_inbox, self.agent1_outbox)
        self.agent2 = Agent(self.agent2_inbox, self.agent2_outbox)
        
        # Message counters
        self.agent1_received = 0
        self.agent2_received = 0
        
        # Event to stop the test
        self.stop_event = asyncio.Event()

    async def asyncTearDown(self):
        pass
        # Clean up files
        #for file in [self.agent1_inbox, self.agent1_outbox]:
        #    if os.path.exists(file):
        #        os.remove(file)

    async def hello_counter_agent_1_handler(self, message):
        if "hello" in message.split():
            self.agent1_received += 1
    
    async def hello_counter_agent_2_handler(self, message):
        if "hello" in message.split():
            self.agent2_received += 1

    async def stop_agent_handler(self, message):
        # allow the message to be processed
        await asyncio.sleep(0.1)
        if self.agent1_received >= 1 and self.agent2_received >= 1:
            self.stop_event.set()


    async def test_two_agent_communication(self):
        self.agent1.register_message_handler(filter_hello_handler)
        self.agent1.register_message_handler(self.hello_counter_agent_1_handler)
        self.agent1.register_message_handler(self.stop_agent_handler)
        self.agent1.register_state_handler(generate_message_every_2_seconds)    

        self.agent2.register_message_handler(filter_hello_handler)
        self.agent2.register_message_handler(self.hello_counter_agent_2_handler)
        self.agent2.register_message_handler(self.stop_agent_handler)
        self.agent2.register_state_handler(generate_message_every_2_seconds)

        # start the agents
        agent1_task = asyncio.create_task(self.agent1.start())
        agent2_task = asyncio.create_task(self.agent2.start())

        try:
            # Wait for the stop event or timeout
            await asyncio.wait_for(self.stop_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            print("Test timed out")
        finally:
            # Cancel tasks
            agent1_task.cancel()
            agent2_task.cancel()
            try:
                await agent1_task
                await agent2_task
            except asyncio.CancelledError:
                pass

        # Count actual "hello" occurrences in files
        agent1_inbox_hellos = 0
        agent2_inbox_hellos = 0

        # Count hellos in agent1's inbox
        if os.path.exists(self.agent1_inbox):
            with open(self.agent1_inbox, 'r') as f:
                agent1_inbox_hellos = sum(1 for line in f if "hello" in line.lower())

        # Count hellos in agent2's inbox
        if os.path.exists(self.agent2_inbox):
            with open(self.agent2_inbox, 'r') as f:
                agent2_inbox_hellos = sum(1 for line in f if "hello" in line.lower())

        # Print results
        print(f"Agent 1 received messages containing 'hello': {self.agent1_received}")
        print(f"Agent 2 received messages containing 'hello': {self.agent2_received}")
        print(f"Agent 1 inbox 'hello' count: {agent1_inbox_hellos}")
        print(f"Agent 2 inbox 'hello' count: {agent2_inbox_hellos}")

        # Verify the counts match
        self.assertEqual(self.agent1_received,  agent1_inbox_hellos, 
                        "Agent 1's received count doesn't match inbox content")
        self.assertEqual(self.agent2_received, agent2_inbox_hellos, 
                        "Agent 2's received count doesn't match inbox content")
        
