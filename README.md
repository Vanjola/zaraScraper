# Zara Scraper Project

## Opis
Ovaj projekat koristi **Selenium** za web scraping na **Zara** sajtu kako bi pratio dostupnost proizvoda sa željenim veličinama, i automatski ih dodavao u korpu. Takođe, šalje **email obavštenja** kada se proizvod sa željenom veličinom doda u korpu.

## Funkcionalnosti
- **Prijava na korisnički nalog**: Automatska prijava na nalog koristeći **email** i **lozinku**.
- **Praćenje favorita**: Skripta pristupa listi omiljenih proizvoda i proverava da li su dostupni u željenim veličinama.
- **Dodavanje u korpu**: Ako je proizvod dostupan u željenoj veličini, automatski se dodaje u korpu.
- **Email obavštenja**: Kada proizvod bude dodat u korpu, korisnik prima email obavštenje.

## Zahtevi
Da bi projekat radio, moraš da imaš sledeće instalirano:

- **Python 3.x**  
- **Selenium**
- **SendGrid API ključ** za slanje emailova
- **.env fajl** sa tvojim podacima (email, lozinka, SendGrid API ključ)

## Instalacija

1. **Kloniraj projekat**:
   ```bash
   git clone https://github.com/korisnickoime/zara-scraper.git
   cd zara-scraper
2. **Kreiraj virtualno okruženje:**
  ```bash
  python -m venv .venv
3. **Aktiviraj virtualno okruženje:**
  ```bash #Na windows
  .\.venv\Scripts\activate


