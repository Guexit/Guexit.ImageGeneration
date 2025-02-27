"""
Unit tests for image generation and services
"""

import os
import sys
import unittest

from tests.image_generation.test_api_models import TestModels
from tests.image_generation.test_api_server import TestServer
from tests.image_generation.test_api_utils import TestAPIUtils
from tests.image_generation.test_core_prompt_crafter import TestPromptCrafter
from tests.image_generation.test_core_schedulers import TestSchedulerHandler
from tests.image_generation.test_core_stable_diffusion_handler import (
    TestStableDiffusionHandler,
)
from tests.image_generation.test_utils import TestUtils
from tests.services.test_image_generation_message_handler import (
    TestImageGenerationMessageHandler,
)
from tests.services.test_message_handlers import (
    TestMessageFactory,
    TestTextToImageMessage,
    TestTextToStyleMessage,
)

assert TestImageGenerationMessageHandler
assert TestStableDiffusionHandler
assert TestSchedulerHandler
assert TestPromptCrafter
assert TestAPIUtils
assert TestServer
assert TestAPIUtils
assert TestModels
assert TestMessageFactory
assert TestTextToStyleMessage
assert TestTextToImageMessage

sys.path.append(os.getcwd())

if __name__ == "__main__":
    unittest.main()
