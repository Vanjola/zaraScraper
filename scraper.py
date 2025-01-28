import os
import time
import random
from mailjet_rest import Client
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import schedule
from selenium.common.exceptions import TimeoutException

load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

mailjet_api_key = os.getenv("MAILJET_API_KEY")
mailjet_api_secret = os.getenv("MAILJET_API_SECRET")

sender_email = os.getenv("SENDER_EMAIL")


def send_email(subject, body, to_email):
    try:
        mailjet = Client(auth=(mailjet_api_key, mailjet_api_secret), version='v3.1')

        data = {
            'Messages': [
                {
                    "From": {
                        "Email": sender_email,
                        "Name": "Zara Bot"
                    },
                    "To": [
                        {
                            "Email": to_email,
                            "Name": to_email
                        }
                    ],
                    "Subject": subject,
                    "TextPart": body
                }
            ]
        }

        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print("Email poslat uspešno preko Mailjet-a!")
        else:
            print(f"Mailjet greška: {result.status_code}, {result.json()}")

    except Exception as e:
        print(f"Greška prilikom slanja email-a: {e}")


def random_sleep(min_sec=1.5, max_sec=3.5):
    """Pomoćna funkcija za nasumično čekanje."""
    time.sleep(random.uniform(min_sec, max_sec))

def type_slowly(element, text, delay=0.1):
    """Simulira unos teksta slovo po slovo."""
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def run_scraper():
    added_sizes = []

    # ChromeOptions za "maskiranje"
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    )
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    driver.get("https://www.zara.com/rs/")
    random_sleep(2, 4)

    # LOGIN deo
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='header-logon-link']"))
        )
        login_button.click()
        random_sleep()
    except Exception as e:
        print(f"Nije pronađen login button: {e}")
        driver.quit()
        return

    try:
        login_button_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='oauth-logon-button']"))
        )
        login_button_2.click()
        random_sleep()
    except Exception as e:
        print(f"Nije pronađen drugi login button: {e}")
        driver.quit()
        return

    try:
        email_label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-input-qualifier='logonId']"))
        )
        type_slowly(email_label, email, delay=0.2)  # Dodaj kašnjenje između slova
        random_sleep()
    except Exception as e:
        print(f"Nije pronađen email input: {e}")
        driver.quit()
        return

    # U delu za unos šifre:
    try:
        password_label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-input-qualifier='password']"))
        )
        type_slowly(password_label, password, delay=0.2)  # Dodaj kašnjenje između slova
        random_sleep()
    except Exception as e:
        print(f"Nije pronađen password input: {e}")
        driver.quit()
        return

    try:
        login_button_final = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "zds-button__lines-wrapper"))
        )
        login_button_final.click()
        random_sleep(2, 5)
    except Exception as e:
        print(f"Nije pronađen final login button: {e}")
        driver.quit()
        return

    # Profil
    try:
        profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='header-user-menu-link']"))
        )
        profile_button.click()
        random_sleep()
    except Exception as e:
        print(f"Nije pronađen profile button: {e}")
        driver.quit()
        return

    # Favorites/Wishlist
    try:
        favorites_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='my-account-wishlist']"))
        )
        favorites_button.click()
        random_sleep()
    except Exception as e:
        print(f"Nije pronađen favorites button: {e}")
        driver.quit()
        return

    random_sleep(2, 4)

    # Sad probamo da pronađemo wishlist grid
    try:
        wishlist_grid = driver.find_element(By.CLASS_NAME, "wishlist-items-grid")
    except Exception as e:
        print(f"Nije pronađen wishlist grid: {e}")
        driver.quit()
        return

    products = wishlist_grid.find_elements(By.CLASS_NAME, "wishlist-item")

    for product in products:
        if "wishlist-item--disabled" not in product.get_attribute("class"):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", product)
                random_sleep()

                # Klik na "Add to bag"
                add_button = product.find_element(
                    By.CSS_SELECTOR, ".wishlist-item-purchase-intention-actions__size-selector-toggle"
                )
                add_button.click()
                random_sleep()

                # Da li proizvod ima veličine?
                size_buttons = product.find_elements(By.CSS_SELECTOR, ".size-selector-list__item-button")

                if not size_buttons:
                    continue

                # Ako ima veličina
                for size in size_buttons:
                    size_label = size.find_element(By.CSS_SELECTOR, "[data-qa-qualifier='product-size-info-main-label']").text.strip()
                    size_action = size.get_attribute("data-qa-action")

                    # Klikćemo samo na veličine sa "size-in-stock" i koje su XS, S, ili 38
                    if size_action == "size-in-stock" and size_label in ["XS", "S", "38"]:
                        size.click()
                        random_sleep()

                        expected_toast_text = f"Veličina {size_label} je dodata u Vašu korpu."

                        try:
                            toast_element = WebDriverWait(driver, 3).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, ".zds-toast-message"))
                            )
                            toast_text = toast_element.text.strip()

                            if expected_toast_text in toast_text:
                                added_sizes.append(size_label)
                                WebDriverWait(driver, 5).until(
                                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".zds-toast-message"))
                                )
                        except TimeoutException:
                            print("WARNING: Toast za veličinu se nije pojavio.")
                        break
            except Exception as e:
                print(f"Greška prilikom obrade proizvoda: {e}")
                continue

    if added_sizes:
        sizes_str = ", ".join(added_sizes)
        subject = "Proizvodi dodati u korpu"
        body = f"Dodate veličine u korpu: {sizes_str}"
        send_email(subject, body, email)

    random_sleep(2, 4)
    driver.quit()


# Automatizacija na svakih 10 minuta
schedule.every(7).minutes.do(run_scraper)

print("Scheduler pokrenut. Skripta će raditi u pozadini...")

while True:
    schedule.run_pending()
    time.sleep(1)
