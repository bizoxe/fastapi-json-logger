"""
This module contains the logging configuration.
"""

from pathlib import Path
import logging.config

import yaml

from core.config import settings


def setup_logging(
    log_dir: Path = settings.log_cfg.log_dir,
    log_level: str = settings.log_cfg.log_level,
    to_file: bool = settings.log_cfg.to_file,
    cfg_yaml: Path = settings.log_cfg.default_log_cfg_yaml,
    env: str = settings.api.environment,
) -> None:
    """
    Basic logging setup.
    Args:
        log_dir: Log file directory.
        log_level: Log level.
        to_file: If true, the logs are written to the file.
        cfg_yaml: Yaml file with settings for logging.
        env: By default dev.
    """
    level = "DEBUG" if env == "dev" else log_level
    with open(cfg_yaml, "rt") as in_f:
        config = yaml.safe_load(in_f)
    config["loggers"]["main"]["level"] = level

    if to_file:
        log_dir.mkdir(exist_ok=True)
        config["handlers"]["queue_handler"]["handlers"].extend(
            ["info_file_handler", "error_file_handler"]
        )

    logging.config.dictConfig(config)
