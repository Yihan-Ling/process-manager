from pathlib import Path
import logging
from process_manager.log.dds_handler import DDSLogHandler

def logger_name(target: str) -> str:
    target_path = Path(target).resolve()
    try:
        # Try to make it relative to the process_manager package
        base = Path(__file__).parent.parent.resolve()
        rpath = target_path.relative_to(base)
        return str(rpath).replace("/", ".").replace("\\", ".").rsplit(".", 1)[0]
    except ValueError:
        # Fall back to just the file stem (name without extension)
        return target_path.stem

def logger(target: Path) -> logging.Logger:
    return logging.getLogger(logger_name(target))

def setup_logging():
    # Set up the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Set up the DDSLogHandler
    dds_handler = DDSLogHandler()
    dds_handler.setLevel(logging.DEBUG)  
    logger.addHandler(dds_handler)  

setup_logging()