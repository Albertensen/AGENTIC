from crewai.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from pydantic import PrivateAttr
import os
import shutil
import tempfile
from webdriver_manager.chrome import ChromeDriverManager

class GeminiChromeBridgeTool(BaseTool):
    name: str = 'gemini_chrome_bridge_tool'
    description: str = 'Berkomunikasi dengan Gemini Pro via browser Chrome (headless) untuk riset data terbaru, outline, dan aset gambar/prompt visual berdasarkan topik yang diberikan.'
    args: dict = {
        'query': {'type': str, 'required': True, 'description': 'Permintaan Agen untuk Gemini Pro'},
        'profile_dir': {'type': str, 'required': True, 'description': 'Profil Chrome yang sudah login (e.g. "Default")'},
        'headless': {'type': bool, 'default': True},
        'wait_timeout': {'type': int, 'default': 60}
    }
    _driver: object = PrivateAttr(default=None)
    _temp_profile_dir: str = PrivateAttr(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._driver = None
        self._temp_profile_dir = None

    def _create_temp_profile(self, profile_dir: str) -> str:
        """Create a temporary copy of the Chrome profile to avoid locking issues."""
        source = fr"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\{profile_dir}"
        if not os.path.exists(source):
            raise FileNotFoundError(f"Profile directory not found: {source}")
        temp_dir = tempfile.mkdtemp(prefix="chrome_profile_")
        dest = os.path.join(temp_dir, profile_dir)
        shutil.copytree(source, dest)
        return temp_dir

    def _get_chrome_options(self, headless: bool, temp_profile_dir: str, profile_dir: str) -> Options:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f"--user-data-dir={temp_profile_dir}")
        chrome_options.add_argument(f"--profile-directory={profile_dir}")
        return chrome_options

    async def _run(self, query: str, profile_dir: str = 'Default', headless: bool = True, wait_timeout: int = 60):
        try:
            # Create temporary profile copy
            self._temp_profile_dir = self._create_temp_profile(profile_dir)
            
            if not self._driver:
                chrome_options = self._get_chrome_options(headless, self._temp_profile_dir, profile_dir)
                service = Service(ChromeDriverManager().install())
                self._driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self._driver.get("https://gemini.google.com/app")
            
            # Wait for the page to load
            WebDriverWait(self._driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Try to find the input box
            input_selectors = [
                (By.ID, "input"),
                (By.XPATH, "//textarea[@placeholder='Ask Gemini...']"),
                (By.XPATH, "//div[contains(@contenteditable, 'true')]"),
                (By.CSS_SELECTOR, "div[role='textbox']"),
            ]
            
            input_box = None
            for by, selector in input_selectors:
                try:
                    input_box = WebDriverWait(self._driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    if input_box:
                        break
                except:
                    continue
            
            if not input_box:
                input_box = self._driver.find_element(By.TAG_NAME, "body")
            
            input_box.clear()
            input_box.send_keys(query)
            input_box.submit()
            
            # Wait for response
            response_selectors = [
                (By.CLASS_NAME, "response-text"),
                (By.XPATH, "//div[contains(@class, 'response')]"),
                (By.XPATH, "//div[contains(@class, 'markdown')]"),
                (By.TAG_NAME, "code"),
            ]
            
            response_element = None
            for by, selector in response_selectors:
                try:
                    def _has_text(driver):
                        el = driver.find_element(by, selector)
                        return el if el.text.strip() else False
                    WebDriverWait(self._driver, wait_timeout).until(_has_text)
                    response_element = self._driver.find_element(by, selector)
                    if response_element and response_element.text.strip():
                        break
                except:
                    continue
            
            if not response_element or not response_element.text.strip():
                return "ERROR: Could not find response element"
            
            response_text = response_element.text.strip()
            return response_text
            
        except TimeoutException:
            return "ERROR: Timeout saat menunggu respons Gemini"
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            print(f"Gemini Chrome Tool Error: {error_msg}")
            try:
                self._driver.quit()
            except:
                pass
            return error_msg
        finally:
            if self._driver:
                self._driver.quit()
            if self._temp_profile_dir and os.path.exists(self._temp_profile_dir):
                try:
                    shutil.rmtree(self._temp_profile_dir)
                except:
                    pass