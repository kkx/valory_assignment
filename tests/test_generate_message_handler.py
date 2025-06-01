import unittest
import asyncio
from io import StringIO
import sys
from generate_message_handler import generate_message_every_2_seconds, WORDS_SOUP

class TestGenerateMessageHandler(unittest.IsolatedAsyncioTestCase):
    
    async def test_message_generation_format(self):
        """Test that generated messages have correct format (two words from WORDS_SOUP)"""
        messages = []
        
        async def test_handler(message):
            messages.append(message)
        
        # Run generator for a shorter time to ensure we get exactly one message
        task = asyncio.create_task(generate_message_every_2_seconds(test_handler))
        await asyncio.sleep(1.9)  # Wait less than 2 seconds to capture only one message
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        # Check we got exactly one message
        self.assertEqual(len(messages), 1, f"Expected 1 message, got {len(messages)}")
        
        # Check message format
        message_words = messages[0].split()
        self.assertEqual(len(message_words), 2)
        self.assertTrue(all(word in WORDS_SOUP for word in message_words))


    async def test_handler_called(self):
        """Test that the handler is called with the generated message"""
        captured_message = None
        
        async def test_handler(message):
            nonlocal captured_message
            captured_message = message
        
        task = asyncio.create_task(generate_message_every_2_seconds(test_handler))
        await asyncio.sleep(2.1)
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        self.assertIsNotNone(captured_message)
        self.assertTrue(all(word in WORDS_SOUP for word in captured_message.split()))


if __name__ == '__main__':
    unittest.main() 