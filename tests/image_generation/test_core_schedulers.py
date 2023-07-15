import unittest
from unittest.mock import MagicMock

from image_generation.core.schedulers import SchedulerHandler


class TestSchedulerHandler(unittest.TestCase):
    def setUp(self):
        # Create a mock for current_scheduler
        self.mock_current_scheduler = MagicMock()

    def test_set_scheduler_with_none(self):
        scheduler = SchedulerHandler.set_scheduler(None, self.mock_current_scheduler)
        self.assertEqual(scheduler, self.mock_current_scheduler)

    def test_set_scheduler_with_invalid_scheduler_name(self):
        with self.assertRaises(ValueError):
            SchedulerHandler.set_scheduler(
                "invalid_scheduler", self.mock_current_scheduler
            )

    def test_set_scheduler_with_valid_scheduler_name(self):
        for scheduler_name, scheduler_class in SchedulerHandler.schedulers.items():
            self.mock_current_scheduler = scheduler_class()
            scheduler = SchedulerHandler.set_scheduler(
                scheduler_name, self.mock_current_scheduler
            )
            self.assertIsNotNone(scheduler)

    def test_set_scheduler_with_same_scheduler(self):
        for scheduler_name, scheduler_class in SchedulerHandler.schedulers.items():
            self.mock_current_scheduler = scheduler_class()
            scheduler = SchedulerHandler.set_scheduler(
                scheduler_name, self.mock_current_scheduler
            )
            self.assertEqual(scheduler, self.mock_current_scheduler)


if __name__ == "__main__":
    unittest.main()
