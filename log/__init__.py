from pathlib import Path
import logging

def logger_name(target: str) -> str:
    rpath = Path(target).resolve().relative_to(Path(__file__).parent.parent)
    parts = list(rpath.parts[:-1]) + [rpath.stem]
    return '.'.join(parts)

def logger(target: Path) -> logging.Logger:
    return logging.getLogger(logger_name(target))