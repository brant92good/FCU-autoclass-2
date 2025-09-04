"""This python file will do the AutoClass job."""
import os
import sys
import time
import signal
import atexit
from os.path import exists

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import utilities as utils

# Setup logging
logger = utils.setup_logger()

config = utils.read_config()
utils.log_info(f"設定檔讀取完成 - 使用者: {config.get('username')}, 課程數量: {len(config.get('class_ids'))}")
utils.log_info(f"目標課程: {', '.join(config.get('class_ids'))}")
utils.log_info(f"無頭模式: {'啟用' if config.get('headless') else '停用'}")

options = webdriver.ChromeOptions()
if config.get("headless"):
    options.add_argument('--headless')
# Add options to prevent orphaned processes
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# Use webdriver-manager to automatically manage ChromeDriver
utils.log_info("正在初始化 Chrome 瀏覽器...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()
utils.log_info("瀏覽器初始化完成")


def kill_chrome_processes():
    """Kill any orphaned Chrome processes."""
    try:
        if os.name == 'nt':  # Windows
            os.system('taskkill /f /im chrome.exe 2>nul')
            os.system('taskkill /f /im chromedriver.exe 2>nul')
        else:  # Linux/Mac
            os.system('pkill -f chrome')
            os.system('pkill -f chromedriver')
    except:
        pass


def cleanup():
    """Clean up resources on exit."""
    global driver
    try:
        if driver:
            utils.log_info("正在清理瀏覽器...")
            print("\nCleaning up browser...")
            # Set a shorter timeout for cleanup to avoid hanging
            driver.set_page_load_timeout(5)
            driver.implicitly_wait(2)
            driver.quit()
            utils.log_info("瀏覽器清理完成")
    except Exception as e:
        utils.log_warning(f"清理瀏覽器時發生錯誤，跳過: {e}")
        # Don't log this as error since it's expected during forced shutdown
    
    # Also kill any orphaned processes
    utils.log_info("正在清理殘留程序...")
    kill_chrome_processes()
    utils.log_info("程序清理完成")


def signal_handler(signum, frame):
    """Handle interrupt signals."""
    utils.log_warning(f"接收到中斷信號 {signum}，正在清理...")
    print(f"\nReceived signal {signum}, cleaning up...")
    
    # Mark driver as None to prevent cleanup from trying to quit it
    global driver
    try:
        if driver:
            # Try a quick cleanup, but don't wait too long
            driver.quit()
    except:
        # Ignore any errors during forced cleanup
        pass
    driver = None
    
    # Kill processes directly
    kill_chrome_processes()
    utils.log_info("程式因中斷信號結束")
    sys.exit(0)


# Register cleanup function to be called on exit
atexit.register(cleanup)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
if hasattr(signal, 'SIGTERM'):
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal


def driver_send_keys(locator, key):
    """Send keys to element.

    :param locator: Locator of element.
    :param key: Keys to send.
    """
    WebDriverWait(driver, 10).until(ec.presence_of_element_located(locator)).send_keys(key)


def driver_click(locator):
    """Click element.

    :param locator: Locator of element.
    """
    WebDriverWait(driver, 10).until(ec.presence_of_element_located(locator)).click()


def driver_screenshot(locator, path):
    """Take screenshot of element.

    :param locator: Locator of element.
    :param path: Path to save screenshot.
    """
    WebDriverWait(driver, 10).until(ec.presence_of_element_located(locator)).screenshot(path)


def driver_get_text(locator):
    """Get text of element.

    :param locator: Locator of element.
    :return: Text of element.
    """
    return WebDriverWait(driver, 10).until(ec.presence_of_element_located(locator)).text


def check_and_close_popup():
    """Check for popup windows and close them."""
    try:
        # 專門處理登入後的調查彈窗
        survey_close_selectors = [
            "//button[@ng-click='surveyCtrl.close($event)']",
            "//button[contains(@class, 'md-icon-button') and contains(@class, 'md-button') and text()='X']",
            "//button[contains(@class, 'md-icon-button') and contains(@ng-click, 'surveyCtrl.close')]"
        ]
        
        for selector in survey_close_selectors:
            try:
                close_button = WebDriverWait(driver, 2).until(
                    ec.element_to_be_clickable((By.XPATH, selector))
                )
                close_button.click()
                utils.log_info(f"✅ 成功關閉登入後調查彈窗，使用選擇器: {selector}")
                time.sleep(0.5)  # Wait a bit after closing
                return True
            except TimeoutException:
                continue
        
        return False
        
    except Exception as e:
        utils.log_error(f"檢查調查彈窗時發生錯誤: {e}")
        return False


def login():
    """Login to FCU course system."""
    global driver
    
    utils.log_info("開始登入 FCU 課程系統...")
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            utils.log_info(f"登入嘗試 {retry_count + 1}/{max_retries}")
            driver.get('https://course.fcu.edu.tw/')
            utils.log_info("已開啟課程系統網頁")
            
            driver_send_keys((By.XPATH, '//*[@id="ctl00_Login1_RadioButtonList1_0"]'), Keys.SPACE)
            utils.log_info("已選擇學生身分")
            
            driver_send_keys((By.ID, "ctl00_Login1_UserName"), config.get("username"))
            utils.log_info("已輸入使用者名稱")
            
            driver_send_keys((By.ID, "ctl00_Login1_Password"), config.get("password"))
            utils.log_info("已輸入密碼")
            
            driver_screenshot((By.ID, "ctl00_Login1_Image1"), "captcha.png")
            utils.log_info("已擷取驗證碼圖片")
            
            ocr_answer = utils.get_ocr_answer("captcha.png")
            utils.log_info(f"OCR 辨識驗證碼: {ocr_answer}")
            
            driver_send_keys((By.ID, "ctl00_Login1_vcode"), ocr_answer)
            utils.log_info("已輸入驗證碼")
            
            driver_click((By.ID, "ctl00_Login1_LoginButton"))
            utils.log_info("已點擊登入按鈕")
            
            # Check if login was successful
            try:
                WebDriverWait(driver, 3).until(ec.presence_of_element_located((By.ID, "ctl00_btnLogout")))
                utils.log_info("登入成功！檢查是否有調查彈窗...")
                
                # Check for survey popup after successful login
                time.sleep(2)  # Wait for any popup to appear
                if check_and_close_popup():
                    utils.log_info("登入後發現並關閉調查彈窗")
                else:
                    utils.log_info("未發現調查彈窗，繼續執行...")
                
                utils.log_info("開始自動加課...")
                print('-------------------------------------')
                print("Login Success. Start auto classing...")
                auto_class(config.get("class_ids"))
                return  # Successfully logged in, exit the function
            except TimeoutException:
                retry_count += 1
                utils.log_warning(f"登入失敗 (第 {retry_count}/{max_retries} 次嘗試)")
                print(f"Login Failed (attempt {retry_count}/{max_retries}), retrying...")
                
                if retry_count < max_retries:
                    # Close current browser and create a new one
                    utils.log_info("關閉當前瀏覽器並建立新實例...")
                    print("Closing current browser and creating new instance...")
                    driver.quit()
                    time.sleep(2)  # Wait a bit before creating new browser
                    
                    # Create new browser instance
                    utils.log_info("建立新的瀏覽器實例...")
                    options = webdriver.ChromeOptions()
                    if config.get("headless"):
                        options.add_argument('--headless')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.maximize_window()
                    utils.log_info("新瀏覽器實例建立完成")
                else:
                    utils.log_error("達到最大登入嘗試次數，程式結束...")
                    print("Max login attempts reached. Exiting...")
                    driver.quit()
                    sys.exit("Login failed after maximum attempts.")
                    
        except Exception as e:
            retry_count += 1
            utils.log_error(f"登入過程中發生未預期錯誤 (第 {retry_count}/{max_retries} 次嘗試): {e}")
            print(f"Unexpected error during login (attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                # Close current browser and create a new one
                utils.log_info("因錯誤關閉當前瀏覽器並建立新實例...")
                print("Closing current browser due to error and creating new instance...")
                try:
                    driver.quit()
                except Exception as quit_error:
                    utils.log_warning(f"關閉瀏覽器時發生錯誤: {quit_error}")
                time.sleep(2)
                
                # Create new browser instance
                utils.log_info("建立新的瀏覽器實例...")
                options = webdriver.ChromeOptions()
                if config.get("headless"):
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.maximize_window()
                utils.log_info("新瀏覽器實例建立完成")
            else:
                utils.log_error("因錯誤達到最大登入嘗試次數，程式結束...")
                print("Max login attempts reached due to errors. Exiting...")
                try:
                    driver.quit()
                except:
                    pass
                sys.exit("Login failed after maximum attempts due to errors.")


def auto_class(class_ids):
    """Auto join class script.

    :param class_ids: List of class ids to join.
    """
    global driver
    
    utils.log_info(f"開始自動加課程序，待加課程: {', '.join(class_ids)}")
    
    while class_ids:
        try:
            utils.log_info("點擊加退選頁面...")
            driver_click((By.ID, "ctl00_MainContent_TabContainer1_tabSelected_Label3"))
            
            for class_id in class_ids[:]:  # create a copy of class_ids for iteration
                try:
                    utils.log_info(f"正在處理課程: {class_id}")
                    driver_send_keys((By.ID, "ctl00_MainContent_TabContainer1_tabSelected_tbSubID"),
                                     class_id)

                    # query remain position
                    utils.log_info(f"查詢課程 {class_id} 剩餘名額...")
                    driver_click((By.XPATH,
                                  "//*[@id='ctl00_MainContent_TabContainer1_tabSelected_gvToAdd']/tbody/tr[2]/td[8]/input"))
                    time.sleep(0.5)
                    alert = driver.switch_to.alert
                    remain_pos = int(alert.text.strip('剩餘名額/開放名額：').split(" /")[0])
                    utils.log_info(f"課程 {class_id}: {alert.text}")
                    print("課程" + class_id + ": " + alert.text)
                    alert.accept()

                    if not remain_pos == 0:
                        utils.log_info(f"課程 {class_id} 有名額，嘗試加選...")
                        driver_click((By.XPATH,
                                      "//*[@id='ctl00_MainContent_TabContainer1_tabSelected_gvToAdd']/tbody/tr[2]/td[1]/input"))
                        result_text = driver_get_text((By.XPATH,
                                            "//*[@id='ctl00_MainContent_TabContainer1_tabSelected_lblMsgBlock']/span"))
                        
                        if result_text == "加選成功":
                            utils.log_info(f"✅ 成功加選課程: {class_id}")
                            print("成功加選課程：" + class_id)
                            class_ids.remove(class_id)
                        else:
                            utils.log_warning(f"❌ 課程 {class_id} 加選失敗: {result_text}")
                            print(
                                "課程" + class_id + ": 加選失敗, 請確認是否已加選或衝堂/超修, 也可能被其他機器人搶走了..")
                    else:
                        utils.log_info(f"課程 {class_id} 無剩餘名額，跳過...")
                    
                    # Small delay between course checks
                    time.sleep(0.5)
                    
                except Exception as e:
                    utils.log_error(f"處理課程 {class_id} 時發生錯誤: {e}")
                    print(f"Error processing class {class_id}: {e}")
                    continue  # Try next class
                    
        except Exception as e:
            utils.log_error(f"自動加課過程中發生嚴重錯誤: {e}")
            print(f"Critical error in auto_class: {e}")
            utils.log_info("嘗試重新啟動瀏覽器並重新登入...")
            print("Attempting to restart browser and re-login...")
            
            # Close current browser
            try:
                driver.quit()
            except Exception as quit_error:
                utils.log_warning(f"關閉瀏覽器時發生錯誤: {quit_error}")
            
            time.sleep(3)  # Wait before restarting
            
            # Create new browser instance
            try:
                utils.log_info("建立新的瀏覽器實例...")
                options = webdriver.ChromeOptions()
                if config.get("headless"):
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.maximize_window()
                utils.log_info("新瀏覽器實例建立完成")
                
                # Re-login
                utils.log_info("重新登入中...")
                print("Re-logging in...")
                login()
                return  # Exit current auto_class call since login() will call auto_class again
                
            except Exception as restart_error:
                utils.log_error(f"重新啟動失敗: {restart_error}")
                print(f"Failed to restart: {restart_error}")
                print("Exiting program...")
                try:
                    driver.quit()
                except:
                    pass
                sys.exit("Critical error: Unable to restart browser.")
        
        # Small delay before next round of checking all classes
        if class_ids:  # Only sleep if there are still classes to check
            utils.log_info(f"等待 2 秒後繼續檢查課程，剩餘課程: {', '.join(class_ids)}")
            time.sleep(2)


if __name__ == "__main__":
    if not exists('./logs'):
        os.makedirs('./logs')
    try:
        utils.log_info("開始執行 FCU AutoClass 程式")
        login()
        utils.log_info("🎉 所有課程加選成功！")
        print("All classes joined successfully!")
    except KeyboardInterrupt:
        utils.log_warning("程式被使用者中斷")
        print("\nProgram interrupted by user.")
    except Exception as e:
        utils.log_error(f"程式發生未預期錯誤: {e}")
        print(f"Unexpected error: {e}")
    finally:
        # cleanup() will be called automatically due to atexit.register()
        utils.log_info("=== FCU AutoClass 程式結束 ===")
        sys.exit("Program finished.")
