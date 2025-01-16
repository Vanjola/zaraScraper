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

1. **Kreiraj virtualno okruženje**:
   ```bash
   python -m venv .v

   ```

2. **Aktiviraj virtualno okruženje**:
   - Na **Windows-u**:
     ```bash
     .\.venv\Scripts\activate
     ```
   - Na **Mac/Linux-u**:
     ```bash
     source .venv/bin/activate
     ```

3. **Instaliraj potrebne biblioteke**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfiguriši `.env` fajl**:
   Kreiraj **`.env`** fajl u korenskom direktorijumu sa sledećim podacima:
   ```txt
   EMAIL=your_email@example.com
   PASSWORD=your_password
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDER_EMAIL=your_send_email@example.com
   SENDER_PASSWORD=your_sender_email_password
   ```

5. **Pokreni aplikaciju**:
   ```bash
   python scraper.py
   ```

Kako funkcioniše
Skripta koristi Selenium za automatsko otvaranje web stranice Zare, prijavu na korisnički nalog i proveru dostupnosti proizvoda u listi omiljenih. 
Kada se nađe proizvod u željenoj veličini, klikne se na njega, dodaje u korpu i šalje obavestenje putem SendGrid-a na zadatu email adresu.

## Licenca

Ovaj projekat je licenciran pod [MIT licencom](LICENSE).





