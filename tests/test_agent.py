import unittest
import asyncio
import os
from pathlib import Path
from agent import Agent

class TestAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Set up test files and agent instance"""
        self.inbox_file = "test_inbox.txt"
        self.outbox_file = "test_outbox.txt"
        self.agent = Agent(self.inbox_file, self.outbox_file)
        
        # Create test files
        Path(self.inbox_file).touch()
        Path(self.outbox_file).touch()

    async def asyncTearDown(self):
        """Clean up test files"""
        for file in [self.inbox_file, self.outbox_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.inbox_file_name, self.inbox_file)
        self.assertEqual(self.agent.outbox_file_name, self.outbox_file)
        self.assertEqual(len(self.agent.message_handlers), 0)
        self.assertEqual(len(self.agent.state_handlers), 0)

    def test_register_handlers(self):
        """Test handler registration"""
        async def test_handler(message): pass
        
        self.agent.register_message_handler(test_handler)
        self.agent.register_state_handler(test_handler)
        
        self.assertEqual(len(self.agent.message_handlers), 1)
        self.assertEqual(len(self.agent.state_handlers), 1)

    async def test_handle_outbox(self):
        """Test outbox message handling"""
        test_message = "test message"
        await self.agent.handle_outbox(test_message)
        
        with open(self.outbox_file, 'r') as f:
            content = f.read().strip()
        self.assertEqual(content, test_message)


    async def test_handle_inbox(self):
        """Test inbox message handling"""
        messages_received = []
        test_complete = asyncio.Event()
        
        async def test_handler(message):
            messages_received.append(message)
            test_complete.set()
        
        self.agent.register_message_handler(test_handler)
        
        # Start the inbox handler first
        task = asyncio.create_task(self.agent.handle_inbox())
        
        # Give the handler a moment to start
        await asyncio.sleep(0.1)
        
        # Then write the test message
        test_message = "test message\n"
        with open(self.inbox_file, 'w') as f:
            f.write(test_message)
            f.flush()
            os.fsync(f.fileno())
        
        try:
            # Wait for the message to be processed or timeout
            await asyncio.wait_for(test_complete.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            print("Timeout waiting for message processing")
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        print(f"messages_received: {messages_received}")
        self.assertEqual(len(messages_received), 1, "No messages were processed")
        self.assertEqual(messages_received[0], test_message, 
                        f"Expected '{test_message}', got '{messages_received[0]}'")

    async def test_start(self):
        """Test agent start method"""
        messages_processed = []
        messages_generated = []
        test_complete = asyncio.Event()
        
        async def test_message_handler(message):
            messages_processed.append(message)
            test_complete.set()
            
        async def test_state_handler(handle_outbox):
            await handle_outbox("test state")
            messages_generated.append("test state")
            test_complete.set()
        
        self.agent.register_message_handler(test_message_handler)
        self.agent.register_state_handler(test_state_handler)
        
        # Write test message to inbox
        with open(self.inbox_file, 'w') as f:
            f.write("test message\n")
            f.flush()
            os.fsync(f.fileno())
        
        # Run agent and wait for completion
        task = asyncio.create_task(self.agent.start())
        
        try:
            # Wait for either message to be processed
            await asyncio.wait_for(test_complete.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            print("Timeout waiting for message processing")
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Check that at least one type of message was processed
        self.assertTrue(
            len(messages_processed) > 0 or len(messages_generated) > 0,
            "No messages were processed or generated"
        )
        
        # Check outbox content if messages were generated
        if messages_generated:
            with open(self.outbox_file, 'r') as f:
                content = f.read().strip()
            self.assertEqual(content, "test state")

    async def test_file_creation(self):
        """Test that files are created if they don't exist"""
        # Remove test files if they exist
        for file in [self.inbox_file, self.outbox_file]:
            if os.path.exists(file):
                os.remove(file)
        
        # Create a simple state handler that will write to outbox
        async def test_state_handler(handle_outbox):
            await handle_outbox("test message")
            
        self.agent.register_state_handler(test_state_handler)
        
        # Start agent briefly
        task = asyncio.create_task(self.agent.start())
        await asyncio.sleep(0.2)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Verify both files exist
        self.assertTrue(os.path.exists(self.inbox_file), "Inbox file was not created")
        self.assertTrue(os.path.exists(self.outbox_file), "Outbox file was not created")

if __name__ == '__main__':
    unittest.main() 