from loguru import logger #Must be first import
from sys import stdout
logger.remove() # remove the default logger

ephemeral_level = logger.level("EPHEMERAL", no=15, color="<yellow>")
report_level = logger.level("REPORT", no=19, color="<yellow>")
approve_level = logger.level("APPROVE", no=22, color="<green>")
remove_level = logger.level("REMOVE", no=22, color="<yellow>")
ban_level = logger.level("BAN", no=24, color="<red>")



fmt = "{time: YYYY-MM-DD HH:mm:ss:SSZZ} | {level: <8} | {name}:{function}:{line} | {message}"
logger.add("localShift.log", retention="30 days", level="INFO", format=fmt, backtrace=True, diagnose=True)


fmt2 = "<green>{time: YYYY-MM-DD HH:mm:ss:SSZZ}</green> | {level: <8} | {message}"
logger.add(stdout,colorize=True, format=fmt2,level="EPHEMERAL")