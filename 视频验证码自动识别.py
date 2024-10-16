from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import ddddocr
import time
import io
from PIL import Image

# 初始化 ddddocr
ocr = ddddocr.DdddOcr()

def connect_to_existing_chrome():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def is_captcha_present(driver):
    try:
        captcha_element = driver.find_element(By.XPATH, '//*[@id="gdImgCode"]')
        return captcha_element.is_displayed()
    except NoSuchElementException:
        return False

def resume_video_playback(driver):
    try:
        video_element = driver.find_element(By.TAG_NAME, 'video')
        driver.execute_script("arguments[0].play();", video_element)
        print("尝试恢复视频播放")
        is_playing = driver.execute_script("return !arguments[0].paused", video_element)
        if is_playing:
            print("视频播放已成功恢复")
        else:
            print("视频播放可能未成功恢复，请检查")
    except Exception as e:
        print(f"恢复视频播放时出错: {str(e)}")

def watch_video_and_handle_captcha(driver, video_url):
    print(f"正在导航到视频页面: {video_url}")
    driver.get(video_url)
    print("开始监控验证码...")

    while True:
        if is_captcha_present(driver):
            print("检测到验证码弹窗")
            try:
                captcha_element = driver.find_element(By.XPATH, '//*[@id="gdImgCode"]')
                
                # 获取验证码图片
                captcha_image = captcha_element.screenshot_as_png
                image = Image.open(io.BytesIO(captcha_image))
                
                # 使用 ddddocr 识别验证码
                captcha_text = ocr.classification(image)
                print(f"识别到的验证码: {captcha_text}")
                
                # 找到验证码输入框并输入识别结果
                input_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="gdCode"]'))
                )
                ActionChains(driver).move_to_element(input_element).click().perform()
                input_element.clear()
                input_element.send_keys(captcha_text)
                
                # 点击确认按钮
                confirm_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="gdVerifyCode"]/a'))
                )
                confirm_button.click()
                
                print("验证码已提交")
                
                # 等待一段时间，确保验证码处理完成
                time.sleep(5)
                
                # 尝试恢复视频播放
                resume_video_playback(driver)
            
            except Exception as e:
                print(f"处理验证码时发生错误: {str(e)}")
                time.sleep(5)
        
        else:
            # 没有检测到验证码弹窗，继续等待
            time.sleep(5)  # 每5秒检查一次
        
        try:
            alert = driver.switch_to.alert
            print(f"检测到警告: {alert.text}")
            alert.accept()
        except:
            pass

def main():
    video_url = "https:"  # 替换为实际的视频URL
    driver = connect_to_existing_chrome()
    try:
        watch_video_and_handle_captcha(driver, video_url)
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        # 不要关闭浏览器，只是断开连接
        driver.quit()

if __name__ == "__main__":
    main()
