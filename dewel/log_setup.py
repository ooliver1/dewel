from logging import INFO, Formatter, StreamHandler, getLogger
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
    formatter = Formatter(
        "%(levelname)-7s %(asctime)s %(filename)12s:%(funcName)-28s: %(message)s",
        datefmt="%H:%M:%S %d/%m/%Y",
    )
    rotating_handler = RotatingFileHandler(
        "./logs/io.log",
        maxBytes=1000000,
        backupCount=5,
        encoding="utf-8",
    )
    rotating_handler.setFormatter(formatter)
    rotating_handler.namer = lambda name: name.replace(".log", "") + ".log"
    stdout_handler = StreamHandler()
    log = getLogger()
    log.handlers = []
    log.setLevel(INFO)

    log.addHandler(rotating_handler)
    log.addHandler(stdout_handler)
    stdout_handler.setFormatter(formatter)
