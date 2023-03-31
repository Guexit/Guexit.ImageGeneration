from enum import Enum
from diffusers.schedulers import (
    EulerAncestralDiscreteScheduler,
    EulerDiscreteScheduler,
    DDIMScheduler,
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
    @classmethod
    def set_scheduler(cls, scheduler_name, current_scheduler):
        optimal_parameters = {}
        logger.info(f"Scheduler name: {scheduler_name}")
        if scheduler_name == SchedulerEnum.EULER_A:
            scheduler_selected = EulerAncestralDiscreteScheduler
            optimal_parameters = {
                "beta_start": 0.00085,
                "beta_end": 0.012,
                "beta_schedule": "scaled_linear",
            }
        elif scheduler_name == SchedulerEnum.EULER:
            scheduler_selected = EulerDiscreteScheduler
        elif scheduler_name == SchedulerEnum.DDIMS:
            scheduler_selected = DDIMScheduler
        elif scheduler_name == SchedulerEnum.PNDM:
            scheduler_selected = PNDMScheduler
        elif scheduler_name is None:
            logger.info("No scheduler selected. Returning default scheduler.")
            return current_scheduler
        else:
            raise ValueError(f"{scheduler_name} is not a valid scheduler")

        if isinstance(current_scheduler, scheduler_selected):
            return current_scheduler
        return scheduler_selected(**optimal_parameters)
