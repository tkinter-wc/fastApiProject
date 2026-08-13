"""
统一日志：模块导入时完成初始化，业务侧直接 from utils.logger import logger
"""

import logging

LOG_FORMAT = "[%(asctime)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
logger.propagate = False  # 避免再冒泡到 root，和 uvicorn 日志重复

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)
