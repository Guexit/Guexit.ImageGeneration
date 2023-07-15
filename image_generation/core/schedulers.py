from enum import Enum

from diffusers.schedulers import (
    DDIMScheduler,
    EulerAncestralDiscreteScheduler,
    EulerDiscreteScheduler,
    PNDMScheduler,
)

from image_generation.custom_logging import set_logger

logger = set_logger("SD Scheduler Handler")


class SchedulerEnum(Enum):
    EULER_A = "euler_a"
    EULER = "euler"
    DDIMS = "ddims"
    PNDM = "pndm"


class SchedulerHandler:
    schedulers = {
        SchedulerEnum.EULER_A.value: EulerAncestralDiscreteScheduler,
        SchedulerEnum.EULER.value: EulerDiscreteScheduler,
        SchedulerEnum.DDIMS.value: DDIMScheduler,
        SchedulerEnum.PNDM.value: PNDMScheduler,
    }

    @classmethod
    def set_scheduler(cls, scheduler_name, current_scheduler):
        optimal_parameters = {
            "beta_start": 0.00085,
            "beta_end": 0.012,
            "beta_schedule": "scaled_linear",
        }

        if scheduler_name is None:
            logger.info("No scheduler selected. Returning default scheduler.")
            return current_scheduler

        scheduler_selected = cls.schedulers.get(scheduler_name)
        if not scheduler_selected:
            valid_schedulers = ", ".join(cls.schedulers.keys())
            raise ValueError(
                f"{scheduler_name} is not a valid scheduler. Valid options are: {valid_schedulers}"
            )

        if isinstance(current_scheduler, scheduler_selected):
            return current_scheduler

        logger.info(f"Using {scheduler_name}")
        return scheduler_selected(**optimal_parameters)
