import time
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule
from selenium.common.exceptions import TimeoutException

load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
api_key = os.getenv("SENDGRID_API_KEY")
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

def send_email(subject, body, to_email):
    sg = sendgrid.SendGridAPIClient(api_key)  # Tvoj API ključ
    from_email = Email(sender_email)          # Tvoj email
    to_email = To(to_email)                   # Email primaoca
    content = Content("text/plain", body)     # Telo poruke
    mail = Mail(from_email, to_email, subject, content)

    try:
        response = sg.send(mail)
        print("Email poslat uspešno!")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.body}")
        print(f"Headers: {response.headers}")
    except Exception as e:
        print(f"Greška prilikom slanja email-a: {e}")

def run_scraper():
    added_sizes = []

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    driver.get("https://www.zara.com/rs/")

    # LOGIN deo
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='header-logon-link']"))
    )
    login_button.click()

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='oauth-logon-button']"))
    )
    login_button.click()

    email_label = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-input-qualifier='logonId']"))
    )
    email_label.send_keys(email)

    password_label = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-input-qualifier='password']"))
    )
    password_label.send_keys(password)

    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "zds-button__lines-wrapper"))
    )
    login_button.click()

    # Profil
    profile_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='header-user-menu-link']"))
    )
    profile_button.click()

    # Favorites/Wishlist
    favorites_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='my-account-wishlist']"))
    )
    favorites_button.click()

    time.sleep(2)

    wishlist_grid = driver.find_element(By.CLASS_NAME, "wishlist-items-grid")
    products = wishlist_grid.find_elements(By.CLASS_NAME, "wishlist-item")

    for product in products:
        if "wishlist-item--disabled" not in product.get_attribute("class"):
            try:
                # Skrol do proizvoda
                driver.execute_script("arguments[0].scrollIntoView(true);", product)
                time.sleep(0.5)

                # Klik na "Add to bag"
                add_button = product.find_element(
                    By.CSS_SELECTOR, ".wishlist-item-purchase-intention-actions__size-selector-toggle"
                )
                add_button.click()

                # Da li proizvod ima veličine?
                size_buttons = product.find_elements(By.CSS_SELECTOR, ".product-size-info__main-label")

                # Ako nema veličina -> verovatno torba
                if not size_buttons:
                    time.sleep(1)
                    try:
                        toast_element = WebDriverWait(driver, 3).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, ".zds-toast-message"))
                        )
                        toast_text = toast_element.text.strip()

                        # Za torbu je toast "Proizvod je dodat u korpu."
                        if "Proizvod je dodat u korpu." in toast_text:
                            # Beležimo "Torba" ili "Proizvod" (kako vam odgovara)
                            added_sizes.append("Torba")

                            # Pokušaj da sačekaš da nestane toast
                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".zds-toast-message"))
                                )
                            except TimeoutException:
                                print("WARNING: Toast za torbu se nije sklonio u roku od 5s, nastavljamo...")

                    except TimeoutException:
                        print("WARNING: Toast za torbu se nije pojavio ili ga nismo prepoznali.")

                    # Prelazimo na sledeći proizvod
                    continue

                # Ako ima veličina -> standardna logika
                for size in size_buttons:
                    size_label = size.text.strip()
                    if size_label in ["XS", "S", "38"]:
                        size.click()
                        time.sleep(1)

                        expected_toast_text = f"Veličina {size_label} je dodata u Vašu korpu."

                        try:
                            toast_element = WebDriverWait(driver, 3).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, ".zds-toast-message"))
                            )
                            toast_text = toast_element.text.strip()

                            if expected_toast_text in toast_text:
                                added_sizes.append(size_label)

                                # Sačekaj da se toast skloni
                                try:
                                    WebDriverWait(driver, 5).until(
                                        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".zds-toast-message"))
                                    )
                                except TimeoutException:
                                    print("WARNING: Toast za veličinu se nije sklonio u roku od 5s, nastavljamo...")

                        except TimeoutException:
                            print("WARNING: Toast za veličinu se nije pojavio ili ga nismo prepoznali.")

                        # Samo jednu veličinu po proizvodu
                        break

            except Exception as e:
                print(f"Greška prilikom obrade proizvoda: {e}")
                continue

    # Ako ima dodatih stavki, šaljemo mail
    if added_sizes:
        sizes_str = ", ".join(added_sizes)
        subject = "Proizvodi dodati u korpu"
        body = f"Dodate veličine (ili torba) u korpu: {sizes_str}"
        send_email(subject, body, email)

    time.sleep(2)
    driver.quit()


# Podesite interval po potrebi
schedule.every(90).seconds.do(run_scraper)

while True:
    schedule.run_pending()
    time.sleep(1)
