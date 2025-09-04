"""This python will handle some extra functions."""
import sys
import os
import logging
from datetime import datetime
from os.path import exists

import ddddocr
import yaml
from yaml import SafeLoader


def setup_logger():
    """Setup logger for the application."""
    # Create logs directory if it doesn't exist
    if not exists('./logs'):
        os.makedirs('./logs')
    
    # Create a timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_filename = f'./logs/logs-{timestamp}.txt'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)  # Also output to console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=== FCU AutoClass 程式啟動 ===")
    return logger


def log_info(message):
    """Log info message."""
    logger = logging.getLogger(__name__)
    logger.info(message)


def log_error(message):
    """Log error message."""
    logger = logging.getLogger(__name__)
    logger.error(message)


def log_warning(message):
    """Log warning message.""" 
    logger = logging.getLogger(__name__)
    logger.warning(message)


def config_file_generator():
    """Generate the template of config file"""
    with open('config.yml', 'w', encoding="utf8") as f:
        f.write("""# ++--------------------------------++
# | FCU-AutoClass                    |
# | Made by LD (MIT License)         |
# ++--------------------------------++

# FCU Account
username: ''
password: ''

# Class to join
# If you have more than one class to join, please separate them with space.
# Example: class_id: '0050 0051'
# The less class_id you have, the more rate you can get the class you want.
class_id: ''

# Headless mode
# If you want to run this script in headless mode, please set this to true.
headless: false
"""
                )
    sys.exit()


def read_config():
    """Read config file.

    Check if config file exists, if not, create one.
    if exists, read config file and return config with dict type.

    :rtype: dict
    """
    if not exists('./config.yml'):
        print("Config file not found, create one by default.\nPlease finish filling config.yml")
        with open('config.yml', 'w', encoding="utf8"):
            config_file_generator()

    try:
        with open('config.yml', 'r', encoding="utf8") as f:
            data = yaml.load(f, Loader=SafeLoader)
            class_ids = get_class_ids(data['class_id'])
            config = {
                'username': data['username'],
                'password': data['password'],
                'class_ids': class_ids,
                'headless': data['headless']
            }
            # Don't log sensitive information like password, only basic info
            print(f"設定檔讀取成功 - 使用者: {config['username']}, 課程數量: {len(class_ids)}")
            return config
    except (KeyError, TypeError) as e:
        error_msg = (
            "讀取 config.yml 時發生錯誤，請檢查檔案是否正確填寫。\n"
            "如果問題無法解決，請考慮刪除 config.yml 並重新啟動程式。\n"
        )
        print(error_msg)
        # Try to log error if logger is available
        try:
            log_error(f"設定檔讀取錯誤: {e}")
        except:
            pass
        sys.exit()


def get_class_ids(class_id):
    """Read class_id from config file.

    :rtype: list
    """
    class_ids = class_id.split(" ")
    return class_ids


def get_ocr_answer(ocr_image_path):
    """Get the answer of ocr.

    :rtype: str
    """
    try:
        log_info(f"開始 OCR 辨識圖片: {ocr_image_path}")
        ocr = ddddocr.DdddOcr()
        with open(ocr_image_path, 'rb') as f:
            image = f.read()
        answer = ocr.classification(image)
        log_info(f"OCR 辨識完成，結果: {answer}")
        return answer
    except Exception as e:
        log_error(f"OCR 辨識失敗: {e}")
        return ""
