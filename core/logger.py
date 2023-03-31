import datetime
import logging
import os
import time
from functools import wraps

# 設定log後綴檔名，log檔名格式為 {%Y-%m-%d}_test.log
LOG_FILENAME = "chat"

"""
1. 自訂logger資訊：
a. 在Python檔案中，引入logger.py：
from utils.logger import create_logger
b. 在程式中添加以下程式碼，建立logger物件：
logger = create_logger()
c. 使用logger物件來寫入log資訊，例如：
logger.info("測試寫入log")
d. 執行後，會在logs資料夾中建立一個名為 %Y-%m-%d_test.log 的log檔案。

2. 使用裝飾器紀錄函數輸入和輸出：
a. 在Python檔案中，引入logger.py：
from utils.logger import log_filter
b. 在要紀錄輸入和輸出的函數上方，添加@log_filter裝飾器，例如：
@log_filter
def test(a):
    ...
c. 執行後，函數的輸入和輸出變數會被記錄到log檔案中。

log_filter用法說明
log_filter: 僅在執行錯誤時會記錄log
log_filter_around: 執行成功會記錄輸入與輸出的變數、執行錯誤時會記錄log、最終結束會記錄時間
"""


def _log_setting(logger):
    """
    logger基本設定
    """
    # 設定logger基本層級
    logger.setLevel('DEBUG')
    # 設定日誌格式
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    consoleHandler = logging.StreamHandler()  # 輸出到控制台的handler
    consoleHandler.setLevel(logging.DEBUG)  # 設定層級(控制台)
    consoleHandler.setFormatter(formatter)  # 設定日誌格式

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    fileHandler = logging.FileHandler(f"./logs/{timestamp}_{LOG_FILENAME}.log", 'a', 'utf-8')  # 輸出到.log的handler
    fileHandler.setLevel(logging.DEBUG)  # 設定層級(.log)
    fileHandler.setFormatter(formatter)  # 設定日誌格式

    # 日誌紀錄器增加此handler
    # 若handler為空，才會添加logger.handlers，避免添加一堆handler重複輸出log
    if not logger.handlers:
        logger.addHandler(consoleHandler)
        logger.addHandler(fileHandler)
    return logger


def create_logger():
    """
    建立logger設定
    :return:
    """
    if not os.path.exists("./logs"):  # 若logs不存在，建立該資料夾
        os.makedirs("./logs")
    # logging.captureWarnings(True)  # 捕捉 py waring message
    logger = logging.getLogger(__name__)  # 設定logging名稱，可以自己改成要用的名稱
    logger = _log_setting(logger)
    return logger


def log_filter(func):
    """
    日誌裝飾器，簡單記錄函數的日誌，僅在執行錯誤時會記錄log
    :param func: 函数
    :return:
    """
    if not os.path.exists("./logs"):  # 若logs不存在，建立該資料夾
        os.makedirs("./logs")
    # 獲得log日誌紀錄器，設定日誌等級
    logger = logging.getLogger(__name__)
    logger = _log_setting(logger)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)  # 無異常就直接return
        except Exception as e:  # 異常才紀錄
            logger.error(f"func: {func.__name__} - error message: {e}", exc_info=True)

    return wrapper


def log_filter_around(func):
    """
    日誌裝飾器，簡單記錄函數的日誌
    執行成功會記錄輸入與輸出的變數、執行錯誤時會記錄log、最終結束會記錄時間
    :param func: 函数
    :return:
    """
    if not os.path.exists("./logs"):  # 若logs不存在，建立該資料夾
        os.makedirs("./logs")
    # 獲得log日誌紀錄器，設定日誌等級
    logger = logging.getLogger(__name__)
    logger = _log_setting(logger)

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            res = func(*args, **kwargs)
            logger.debug(f"func: {func.__name__} - input: {args, kwargs} -> output: {res}")
            return res
        except Exception as e:
            logger.error(f"func: {func.__name__} - error message: {e}", exc_info=True)
        finally:
            logger.debug(f"func: {func.__name__} - time: {round(time.time() - start_time, 2)} sec.")

    return wrapper
