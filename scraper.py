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


load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
api_key = os.getenv("SENDGRID_API_KEY")
sender_email=os.getenv("SENDER_EMAIL")
sender_password=os.getenv("SENDER_PASSWORD")


def send_email(subject, body, to_email):
    sg = sendgrid.SendGridAPIClient(api_key)  # Koristi svoj API ključ
    from_email = Email(sender_email)  # Tvoj email
    to_email = To(to_email)  # Email primaoca
    content = Content("text/plain", body)  # Telo poruke
    mail = Mail(from_email, to_email, subject, content)

    try:
        response = sg.send(mail)
        print("Email poslat uspešno!")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.body}")
        print(f"Headers: {response.headers}")
    except Exception as e:
        print(f"Greška prilikom slanja email-a: {e}")


# Funkcija koju želimo da pokrećemo svakih 3 minuta
def run_scraper():
    # Pokrećemo Chrome browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.maximize_window()

    # Otvaramo stranicu
    driver.get("https://www.zara.com/rs/")

    # Čekamo da se dugme za prijavu učita
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='header-logon-link']"))
    )
    login_button.click()

    # Čekamo da se dugme za prijavu na sledećoj stranici učita
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='oauth-logon-button']"))
    )
    login_button.click()

    # Čekamo da se polje za email pojavi i unosimo email
    email_label = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-input-qualifier='logonId']"))
    )
    email_label.send_keys(email)

    # Čekamo da se polje za lozinku pojavi i unosimo lozinku
    password_label = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-qa-input-qualifier='password']"))
    )
    password_label.send_keys(password)

    # Čekamo dugme za login i klikćemo na njega
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "zds-button__lines-wrapper"))
    )
    login_button.click()

    # Čekamo da se stranica za profil učita pre nego što kliknemo na dugme
    profile_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='header-user-menu-link']"))
    )
    profile_button.click()

    # Čekamo da stranica za Favorites bude dostupna
    favorites_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-qa-id='my-account-wishlist']"))
    )
    favorites_button.click()

    time.sleep(2)

    wishlist_grid = driver.find_element(By.CLASS_NAME, "wishlist-items-grid")
    products = wishlist_grid.find_elements(By.CLASS_NAME, "wishlist-item")

    for product in products:
        if "wishlist-item--disabled" not in product.get_attribute("class"):
            add_button = product.find_element(By.CSS_SELECTOR, ".wishlist-item-purchase-intention-actions__size-selector-toggle")
            add_button.click()

            size_buttons = driver.find_elements(By.CSS_SELECTOR, ".product-size-info__main-label")
            for size in size_buttons:
                size_label = size.text  # Dohvatamo tekst veličine (npr. XS, S, itd.)
                if size_label in ["XS", "S", "38"]:  # Ako veličina odgovara željenoj
                    size.click()  # Kliknemo na veličinu
                    print(f"Veličina {size_label} selektovana!")
                    subject = "Proizvod dodat u korpu"
                    body = f"Proizvod sa veličinom {size_label} je uspešno dodat u korpu."
                    to_email = email # Unesi svoj email
                    send_email(subject, body, to_email)
                    break

    time.sleep(4)
    # Zatvaramo browser
    driver.quit()


# Postavljanje zadatka da se izvršava svakih 3 minuta
schedule.every(90).seconds.do(run_scraper)

# Stalna petlja koja proverava kada treba da pokrene zadatke
while True:
    schedule.run_pending()  # Pokreće sve zakazane zadatke koji su sada na redu
    time.sleep(1)  # Pauza od 1 sekunde da bi sistem mogao da proverava
