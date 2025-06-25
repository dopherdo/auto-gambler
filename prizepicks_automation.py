import time
import pickle
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from PIL import Image
import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class PrizePicksAutomation:
    def __init__(self, headless=False):
        self.driver = None
        self.headless = headless
        self.wait = None
        
    def setup_driver(self):
        """Initialize the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to appear more human-like
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property to avoid detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        self.wait = WebDriverWait(self.driver, config.ELEMENT_WAIT_TIMEOUT)
        
        logger.info("Chrome WebDriver initialized successfully")
        
    def load_cookies(self):
        """Load saved cookies if they exist."""
        if os.path.exists(config.COOKIES_FILE):
            try:
                cookies = pickle.load(open(config.COOKIES_FILE, "rb"))
                self.driver.get(config.PRIZEPICKS_URL)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                logger.info("Cookies loaded successfully")
                return True
            except Exception as e:
                logger.error(f"Error loading cookies: {e}")
        return False
    
    def save_cookies(self):
        """Save current cookies for future sessions."""
        try:
            cookies = self.driver.get_cookies()
            pickle.dump(cookies, open(config.COOKIES_FILE, "wb"))
            logger.info("Cookies saved successfully")
        except Exception as e:
            logger.error(f"Error saving cookies: {e}")
    
    def login(self):
        """Login to PrizePicks if not already logged in."""
        try:
            self.driver.get(config.PRIZEPICKS_LOGIN_URL)
            
            # Check if already logged in by looking for logout button or user menu
            if self.is_logged_in():
                logger.info("Already logged in to PrizePicks")
                return True
            
            # Find and fill email field
            email_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']"))
            )
            email_field.clear()
            email_field.send_keys(config.PRIZEPICKS_EMAIL)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            password_field.clear()
            password_field.send_keys(config.PRIZEPICKS_PASSWORD)
            
            # Find and click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .login-button, [data-testid='login-button']")
            login_button.click()
            
            # Wait for successful login
            self.wait.until(lambda driver: self.is_logged_in())
            
            # Save cookies for future sessions
            self.save_cookies()
            
            logger.info("Successfully logged in to PrizePicks")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def is_logged_in(self):
        """Check if user is logged in by looking for common logged-in indicators."""
        try:
            # Look for elements that indicate user is logged in
            indicators = [
                "button[data-testid='logout']",
                ".user-menu",
                ".profile-button",
                "[data-testid='user-menu']",
                ".account-menu"
            ]
            
            for indicator in indicators:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, indicator)
                    return True
                except NoSuchElementException:
                    continue
            
            return False
        except:
            return False
    
    def navigate_to_link(self, link):
        """Navigate to a PrizePicks link that should populate the slip builder."""
        try:
            logger.info(f"Navigating to: {link}")
            self.driver.get(link)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for slip builder to populate (look for common slip elements)
            slip_indicators = [
                ".slip-builder",
                "[data-testid='slip-builder']",
                ".bet-slip",
                ".slip-container"
            ]
            
            slip_found = False
            for indicator in slip_indicators:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, indicator)))
                    slip_found = True
                    logger.info("Slip builder populated successfully")
                    break
                except TimeoutException:
                    continue
            
            if not slip_found:
                logger.warning("Slip builder elements not found - link may not have populated correctly")
            
            return slip_found
            
        except Exception as e:
            logger.error(f"Error navigating to link: {e}")
            return False
    
    def submit_slip(self):
        """Submit the current slip with verification."""
        try:
            # Look for submit button with various possible selectors
            submit_selectors = [
                "button[data-testid='submit-slip']",
                ".submit-slip-button",
                "button:contains('Submit')",
                "[data-testid='submit-button']",
                ".submit-button",
                "button[type='submit']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not submit_button:
                logger.error("Submit button not found")
                return False
            
            # Take screenshot before submission for verification
            if config.SCREENSHOT_ON_SUBMISSION:
                self.take_screenshot("before_submission")
            
            # Click submit button
            logger.info("Clicking submit button...")
            submit_button.click()
            
            # Wait for submission delay
            time.sleep(config.SUBMISSION_DELAY)
            
            # Take screenshot after submission
            if config.SCREENSHOT_ON_SUBMISSION:
                self.take_screenshot("after_submission")
            
            # Verify submission was successful
            success = self.verify_submission()
            
            if success:
                logger.info("Slip submitted successfully!")
            else:
                logger.warning("Submission verification failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error submitting slip: {e}")
            return False
    
    def verify_submission(self):
        """Verify that the slip was submitted successfully."""
        try:
            # Look for success indicators
            success_indicators = [
                ".success-message",
                "[data-testid='success-message']",
                ".confirmation-message",
                ".submission-success",
                "div:contains('Success')",
                "div:contains('Submitted')"
            ]
            
            for indicator in success_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        logger.info("Success indicator found")
                        return True
                except NoSuchElementException:
                    continue
            
            # Check if slip builder is empty (indicating successful submission)
            try:
                slip_builder = self.driver.find_element(By.CSS_SELECTOR, ".slip-builder, [data-testid='slip-builder']")
                if "empty" in slip_builder.get_attribute("class") or not slip_builder.text.strip():
                    logger.info("Slip builder appears empty - submission likely successful")
                    return True
            except:
                pass
            
            logger.warning("No clear success indicators found")
            return False
            
        except Exception as e:
            logger.error(f"Error during submission verification: {e}")
            return False
    
    def take_screenshot(self, name):
        """Take a screenshot for verification purposes."""
        try:
            if not os.path.exists(config.SCREENSHOTS_DIR):
                os.makedirs(config.SCREENSHOTS_DIR)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{config.SCREENSHOTS_DIR}/{name}_{timestamp}.png"
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
    
    def close(self):
        """Close the browser and clean up."""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed") 