#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import sys
from time import sleep
import psutil
from common_lib.common_error import BadUserInputError
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import  DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.common.options import ArgOptions
from common_lib.otp_helper import OtpHelper
from exceptions.aws_sso_user_core_authorization_error import AwsSsoUserCodeAuthorizationException
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from common_lib.enum_browser_type import BrowserType
from common_lib.os_process_helper import OsProcessHelper
import socket

class SeleniumAwsAppLogin(object):
  """
      SeleniumSsoLogin login on aws from sso portal
      @params:
          aws_username                            - Required  : aws user name for login
          aws_password                            - Required  : aws user password for login
          user_code                               - Required  : user account genetared from sso_oidc.start_device_authorization service
          aws_start_url                           - Required  : aws url for login
          aws_otp_device_id                       - Optional  : aws otp device id to genetare 2fa code
          debug                                   - Optional  : debug flag with default = False, if True, will sholl egde browser, if not set will be False
      """
  
  SUBMIT_BUTTON_ELEMENT = "//button[@type='submit']"
  DEBUG_PORT=9222
  WEBDRIVER_DEBUG_ARGS= f"--port={DEBUG_PORT}"


  def __init__(self, 
                aws_username:str,
                aws_password:str,
                aws_start_url:str,
                browser:BrowserType,
                otp_2fa_devide_id:str = None,
                debug:bool = False) -> None:

    self._aws_username:str = aws_username
    self._aws_password:str = aws_password
    self._aws_start_url:str = aws_start_url
    self._otp_2fa_devide_id:str = otp_2fa_devide_id
    self.browser = browser
    self._debug:bool = debug
    self.browser_path:str = None
    self.selenium_driver_path:str = None
    self.browser_name = None
    self.os_process_helper:OsProcessHelper = None
    self._set_browser()

  def _set_browser(self) -> None:
    self.browser_name = None
    browser_path_variable_name = None
    selenium_driver_path_variable_name = None
    if self.browser == BrowserType.CHROME:
      self.browser_name = 'chrome'
      browser_path_variable_name = "CHROME_BROWSER_PATH"
      selenium_driver_path_variable_name = "CHROME_DRIVER_PATH"
      
    elif self.browser == BrowserType.EDGE:
      self.browser_name = 'msedge'
      browser_path_variable_name = "EDGE_BROWSER_PATH"
      selenium_driver_path_variable_name = "EDGE_DRIVER_PATH"
      
    elif self.browser == BrowserType.FIREFOX:
      self.browser_name = 'firefox'
      browser_path_variable_name = "FIREFOX_BROWSER_PATH"
      selenium_driver_path_variable_name = "FIREFOX_DRIVER_PATH"
    
    if sys.platform != "win32":
      if browser_path_variable_name not in os.environ:
        raise BadUserInputError(f"The environment variable {browser_path_variable_name} not set.")
      self.browser_path = os.environ[browser_path_variable_name]
      if not os.path.exists(browser_path_variable_name):
        BadUserInputError(f"Browser {self.browser_name} not found on {browser_path_variable_name}")

    if selenium_driver_path_variable_name not in os.environ:
      raise BadUserInputError(f"The environment variable {selenium_driver_path_variable_name} not set.")
    
    self.selenium_driver_path = os.environ[selenium_driver_path_variable_name]

    if not os.path.exists(selenium_driver_path_variable_name):
      BadUserInputError(f"{self.browser_name} driver {selenium_driver_path_variable_name} not found")

  def check_exists_by_xpath(self, browser: webdriver.Edge, xpath):
    try:
        browser.find_element(by= By.XPATH, value=xpath)
    except NoSuchElementException:
        return False
    return True

  def _get_webdriver_process_info(self, 
                                    debug_args:str) -> dict:
    process_info: dict = None
    for proc in psutil.process_iter():
      try:
        pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
        if (pinfo["cmdline"] is not None and 
            len(pinfo["cmdline"])> 0 and 
            debug_args in pinfo["cmdline"]):
          process_info = pinfo
          break
      except (psutil.NoSuchProcess, IndexError, TypeError):
        pass
    return process_info

  def _check_webdriver_alread_opened(self, 
                                    debug_args:str) -> bool:
    return False if self._get_webdriver_process_info(debug_args) is None else True

 
  def _start_detached_webdriver(self) -> None:
    if sys.platform == "win32":
      command="cmd"
    else:
      command="nohup"
    
    args=[]
    
    if sys.platform == "win32":
      args.extend(["/c", self.selenium_driver_path, f"--port={self.DEBUG_PORT}"])
    else:
      args.extend([self.selenium_driver_path, f"--port={self.DEBUG_PORT}"])
    
    args.extend([self.WEBDRIVER_DEBUG_ARGS])
    
    if not self._check_webdriver_alread_opened(debug_args=self.WEBDRIVER_DEBUG_ARGS):
      self.os_process_helper = OsProcessHelper(command=command, args=args)
      self.os_process_helper.start()
    
  def _check_debug_port_opened(self) -> bool:
    """_summary_

    Returns:
        bool: _description_
    """
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    location = ("127.0.0.1", self.DEBUG_PORT)
    check = a_socket.connect_ex(location)

    return (check == 0)

  def _get_web_driver(self) -> RemoteWebDriver:
    """
    
    """
    url_webdriver=f"http://localhost:{self.DEBUG_PORT}"
    driver:RemoteWebDriver = None
    if self.browser == BrowserType.CHROME:
      driver = webdriver.Remote(command_executor=url_webdriver ,desired_capabilities=DesiredCapabilities.CHROME)
    elif self.browser == BrowserType.EDGE:
      driver = webdriver.Remote(command_executor=url_webdriver ,desired_capabilities=DesiredCapabilities.EDGE)
    elif self.browser == BrowserType.FIREFOX:
      driver = webdriver.Remote(command_executor=url_webdriver ,desired_capabilities=DesiredCapabilities.FIREFOX)
    return driver

  def login(self) -> None:

    self._start_detached_webdriver()
    driver = self._get_web_driver()
    driver.maximize_window()
    
    while(not self._check_debug_port_opened()):
      print("waiting for remote debug")
      sleep(1000)
      
    driver.get(self._aws_start_url)

    wait = WebDriverWait(driver, 30)
    
    try:
        wait.until(EC.visibility_of_any_elements_located((By.ID, 'awsui-input-0')))
    except TimeoutException as ex: 
        if self.check_exists_by_xpath(browser=driver, xpath="//b[contains(.,'Authorization failed')]"):
            driver.close()
            raise AwsSsoUserCodeAuthorizationException()
        else:
            raise ex
        
    driver.find_element(by= By.ID, value="awsui-input-0").send_keys(self._aws_username)
    driver.find_element(by= By.XPATH, value=self.SUBMIT_BUTTON_ELEMENT).click()

    wait.until(EC.visibility_of_any_elements_located((By.ID, 'password-input')))
    driver.find_element(by= By.ID, value='awsui-input-1').send_keys(self._aws_password)
    driver.find_element(by= By.XPATH, value=self.SUBMIT_BUTTON_ELEMENT).click()

    if self._otp_2fa_devide_id is not None:
      try:
        wait.until(EC.visibility_of_any_elements_located((By.ID, 'awsui-input-0')))
        otp_helper = OtpHelper(self._otp_2fa_devide_id)
        driver.find_element(by= By.ID, value='awsui-input-0').send_keys(otp_helper.get_code())
        driver.find_element(by= By.XPATH, value=self.SUBMIT_BUTTON_ELEMENT).click()
      except TimeoutException as ex: 
          if self.check_exists_by_xpath(browser=driver, xpath="//b[contains(.,'Authorization failed')]"):
              driver.close()
              raise AwsSsoUserCodeAuthorizationException()


    process_info = self._get_webdriver_process_info(self.WEBDRIVER_DEBUG_ARGS)
    if process_info and "pid" in process_info:
      self.os_process_helper.kill(process_info["pid"])
    
    self.os_process_helper.finish()

    # wait.until(EC.visibility_of_any_elements_located((By.CLASS_NAME, 'user-display-name')))
    # driver.close()
    
        
    
    
