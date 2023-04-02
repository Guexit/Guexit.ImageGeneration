"""
Unit tests for image generation and services
"""

import unittest

import os
import sys

from tests.services.test_image_generation_message_handler import (
    TestImageGenerationMessageHandler,
)

assert TestImageGenerationMessageHandler

sys.path.append(os.getcwd())

if __name__ == "__main__":
    unittest.main()
