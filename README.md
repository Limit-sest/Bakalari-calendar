# Bakaláři Kalendář

Tento projekt umožňuje export rozvrhu ze systému Bakaláři do formátu iCal (.ics), který je možné následně přidat do kalendářových aplikací, jako je Google Calendar, Apple Calendar nebo Microsoft Outlook.

## **Instalace**

Nejdříve nainstalujte všechny požadované balíčky pomocí příkazu

```bash
pip install ics arrow requests dotenv
```

## **Co je iCal soubor?**

iCal (nebo také iCalendar) je standardní formát pro sdílení informací o událostech, úkolech a dalších kalendářových datech mezi různými aplikacemi. Tyto soubory mají obvykle příponu `.ics` a jsou široce podporované kalendářovými aplikacemi.

### **Jak vytvořit iCal soubor dostupný na internetu?**

1. **Vytvoření .ics souboru** – Tento projekt generuje `.ics` soubor, který obsahuje všechny informace o rozvrhu z Bakalářů.
2. **Nahrání na veřejně přístupné místo** – Nahrajte soubor na server, který umožňuje přístup přes HTTP nebo HTTPS (např. na vlastní webhosting, nebo služby jako Dropbox či Google Drive).
3. **Získání URL souboru** – Jakmile je soubor nahrán, získáte URL adresu, kterou můžete sdílet s ostatními. Tuto URL adresu můžete také přidat přímo do vaší kalendářové aplikace, která bude iCal soubor synchronizovat.
