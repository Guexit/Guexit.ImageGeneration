"""
Unit tests for image generation and services
"""

import os
import sys
import unittest

from tests.services.test_image_generation_message_handler import (
    TestImageGenerationMessageHandler,
)

assert TestImageGenerationMessageHandler

sys.path.append(os.getcwd())

if __name__ == "__main__":
    unittest.main()
