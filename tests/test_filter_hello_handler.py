import unittest
import asyncio
import sys
from io import StringIO
from filter_hello_handler import filter_hello_handler

class TestFilterHelloHandler(unittest.IsolatedAsyncioTestCase):
    
    async def test_filter_hello_handler_with_hello(self):
        """Test that handler prints messages containing 'hello'"""
        message = "hello world"
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        await filter_hello_handler(message)
        sys.stdout = sys.__stdout__
        
        self.assertIn("hello world", captured_output.getvalue())

    async def test_filter_hello_handler_without_hello(self):
        """Test that handler ignores messages without 'hello'"""
        message = "hi world"
        captured_output = StringIO()
        sys.stdout = captured_output
        
        await filter_hello_handler(message)
        sys.stdout = sys.__stdout__
        
        self.assertEqual(captured_output.getvalue(), "")

    async def test_filter_hello_handler_with_hello_in_middle(self):
        """Test that handler detects 'hello' anywhere in the message"""
        message = "say hello to everyone"
        captured_output = StringIO()
        sys.stdout = captured_output
        
        await filter_hello_handler(message)
        sys.stdout = sys.__stdout__
        
        self.assertIn("say hello to everyone", captured_output.getvalue())

    async def test_filter_hello_handler_empty_message(self):
        """Test handler with empty message"""
        message = ""
        captured_output = StringIO()
        sys.stdout = captured_output
        
        await filter_hello_handler(message)
        sys.stdout = sys.__stdout__
        
        self.assertEqual(captured_output.getvalue(), "")

if __name__ == '__main__':
    unittest.main()