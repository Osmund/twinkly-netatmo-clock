# Netatmo til Twinkly Square Display / Netatmo to Twinkly Square Display

[🇳🇴 Norsk](#norsk) | [🇬🇧 English](#english)

---

## Norsk

Dette prosjektet viser temperatur fra Netatmo værstasjon, Yr utetemperatur og strømpriser på en Twinkly Square LED-display.

### Funksjoner

- 🌡️ Henter sanntidstemperatur fra Netatmo API
- ☀️ Henter utetemperatur fra Yr (Sokndal)
- ⚡ Henter strømpriser fra Hvakosterstrommen.no (NO2 - Sør-Norge)
- 💡 Viser temperaturen på Twinkly Square med fargekoding:
  - **Temperatur:**
    - Blå: Under 0°C
    - Lyseblå: 0-10°C
    - Gul: 10-20°C
    - Rød/Oransje: Over 20°C
  - **Strømpris:**
    - Grønn: Under 50 øre/kWh
    - Gul: 50-100 øre/kWh
    - Rød: Over 100 øre/kWh
- 🎨 Unike ikoner for hver lokasjon (Stue, Kjøkken, Kjeller, Loft, Ute, Strøm)
- 🔄 Automatisk rotasjon mellom alle lokasjoner
- 🕐 Digital klokke med farger som endres gjennom døgnet
- �️ Væranimasjoner basert på Yr data:
  - ☀️ Sol: Pulserende sol med stråler
  - 🌧️ Regn: Regndrøper som faller nedover
  - ❄️ Snø: Snøfnugg som driver sakte nedover
  - ⛈️ Torden: Lynstråler og hvite blinkende blitz
  - 🌫️ Tåke: Bevegelige tåkebanker
  - ⚡💰 Strømvarsel: Blinkende rød skjerm når strømprisen er over 100 øre/kWh
- �🌐 Web-grensesnitt på port 8080 for kontroll og overvåking
- 🎨 Visuell ikon-editor (24x16 grid) for å lage og redigere ikoner
- 🔐 OAuth2 autentisering med automatisk token refresh

### Forutsetninger

- Python 3.7 eller nyere
- En Netatmo værstasjon med tilkoblet konto
- En Twinkly Square LED-display på samme nettverk
- Netatmo Developer App (for API tilgang)
- Git (for kloning av repository)
- Linux-system med systemd (for automatisk oppstart)

### Installasjon

#### 1. Klon repository

```bash
cd ~
git clone <repository-url> "Twinkly Square"
cd "Twinkly Square"
```

#### 2. Opprett virtuelt miljø

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Installer avhengigheter

```bash
pip install -r requirements.txt
```

#### 4. Sett opp Netatmo Developer App

1. Gå til [Netatmo Developer Portal](https://dev.netatmo.com/)
2. Logg inn med din Netatmo-konto
3. Opprett en ny app:
   - Klikk på "Create" eller "Create an app"
   - Fyll ut nødvendig informasjon (navn, beskrivelse, etc.)
   - Etter opprettelse, noter ned:
     - **Client ID**
     - **Client Secret**

#### 5. Opprett konfigurasjonsfil

Opprett en `.env` fil i prosjektmappen:

```bash
nano .env
```

Fyll inn følgende innhold:

```env
# Netatmo API credentials (fra Developer Portal)
NETATMO_CLIENT_ID=din_client_id_her
NETATMO_CLIENT_SECRET=din_client_secret_her

# Ditt Netatmo brukernavn og passord
NETATMO_USERNAME=din_epost@example.com
NETATMO_PASSWORD=ditt_passord

# Twinkly Square IP-adresse (la stå tom for auto-discovery)
TWINKLY_IP=

# Oppdateringsintervall i sekunder (valgfritt, standard 60)
UPDATE_SECONDS=60
```

**Tips for å finne Twinkly IP-adresse:**
- Sjekk din router for tilkoblede enheter
- Bruk Twinkly appen på mobilen (se i innstillinger)
- La feltet stå tomt, så vil scriptet forsøke å finne den automatisk

#### 6. Test installasjon

Kjør programmet manuelt for å teste:

```bash
python3 main.py
```

Programmet vil:
1. Koble til Netatmo API og autentisere
2. Hente utetemperatur fra Yr (Sokndal)
3. Hente strømpris fra Hvakosterstrommen.no (NO2)
4. Finne og koble til Twinkly Square
5. Vise temperaturer og strømpris på displayet
6. Rotere mellom alle lokasjoner med valgt intervall

Trykk `Ctrl+C` for å stoppe.

#### 7. Sett opp systemd services (valgfritt - for automatisk oppstart)

Rediger service-filene for å matche din bruker og sti:

```bash
# Rediger display service
nano twinkly-display.service
# Endre User=admog til din bruker
# Endre WorkingDirectory til din sti

# Rediger web service
nano twinkly-web.service
# Endre User=admog til din bruker
# Endre WorkingDirectory til din sti
```

Installer og aktiver services:

```bash
# Kopier service-filer
sudo cp twinkly-display.service /etc/systemd/system/
sudo cp twinkly-web.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Aktiver services for automatisk oppstart
sudo systemctl enable twinkly-display.service
sudo systemctl enable twinkly-web.service

# Start services
sudo systemctl start twinkly-display.service
sudo systemctl start twinkly-web.service

# Sjekk status
sudo systemctl status twinkly-display.service
sudo systemctl status twinkly-web.service
```

### Bruk

#### Manuell kjøring

```bash
cd "Twinkly Square"
source .venv/bin/activate
python3 main.py
```

#### Web-grensesnitt

Åpne nettleser på `http://<din-ip>:8080` for å:
- **Se alle temperaturer og strømpris live** - Sanntidsdata fra alle sensorer
- **Bytte mellom rotering og enkelt visning** - Roter automatisk mellom lokasjoner eller velg en fast visning
- **Velge spesifikk lokasjon** - Vis kun én lokasjon (Stue, Kjøkken, Kjeller, Loft, Ute eller Strømpris)
- **Justere oppdateringsintervall** - Velg mellom 5-300 sekunder for hvor ofte displayet skal oppdatere data
- **Slå klokke på/av** - Vis en digital klokke på displayet med vakre farger som endres gjennom døgnet
- **Starte/stoppe displayet** - Full kontroll over displayets tilstand
- **Koble til Twinkly på nytt** - Manuell reconnect-knapp hvis Twinkly har vært frakoblet (f.eks. etter strømbrudd)

Webgrensesnittet har et moderne, responsivt design som fungerer på både desktop og mobil. All kontroll skjer i sanntid uten behov for å restarte programmet.

**Automatisk reconnect:** Programmet prøver automatisk å koble til Twinkly ved oppstart (10 forsøk × 3s) og ved tilkoblingsfeil under kjøring (5 forsøk × 2s). Hvis Twinkly har vært frakoblet lenger, kan du bruke reconnect-knappen i webgrensesnittet.

#### Ikon-editor

For å lage eller redigere ikoner, kjør ikon-editoren:

```bash
cd "Twinkly Square"
source .venv/bin/activate
python3 icon_editor.py
```

Åpne nettleser på `http://<din-ip>:5000` for å:
- **Tegne ikoner** - Bruk et 24x16 grid for å lage pikselmønstre
- **Laste inn eksisterende ikoner** - Rediger ikoner som allerede finnes
- **Lagre ikoner** - Lagrer direkte til `icons.py` for umiddelbar bruk
- **Slette ikoner** - Fjern ikoner du ikke trenger

Ikon-editoren har:
- Klikk for å tegne, høyreklikk eller Shift+klikk for å slette
- Dra med musen for å tegne/slette flere piksler
- Live forhåndsvisning av alle ikoner
- Responsivt design for desktop og mobil

#### Systemd service kommandoer

```bash
# Start services
sudo systemctl start twinkly-display.service
sudo systemctl start twinkly-web.service

# Stopp services
sudo systemctl stop twinkly-display.service
sudo systemctl stop twinkly-web.service

# Restart services
sudo systemctl restart twinkly-display.service
sudo systemctl restart twinkly-web.service

# Sjekk status
sudo systemctl status twinkly-display.service
sudo systemctl status twinkly-web.service

# Se logger
sudo journalctl -u twinkly-display.service -f
sudo journalctl -u twinkly-web.service -f
```

### Prosjektstruktur

```
.
├── main.py                 # Hovedprogram
├── netatmo_client.py       # Netatmo API klient
├── yr_client.py            # Yr API klient (MET Norway)
├── electricity_client.py   # Strømpris API klient
├── twinkly_client.py       # Twinkly Square kontroller
├── icons.py                # Ikoner for lokasjoner
├── web_server.py           # Flask webserver
├── icon_editor.py          # Visuell ikon-editor
├── cleanup_display.py      # Cleanup script
├── templates/
│   ├── index.html         # Web-grensesnitt
│   └── icon_editor.html   # Ikon-editor grensesnitt
├── requirements.txt        # Python avhengigheter
├── .env                    # Din konfigurasjon (ikke commit!)
├── display_state.json      # State persistence (genereres automatisk)
├── twinkly-display.service # Systemd service (display)
├── twinkly-web.service     # Systemd service (web)
└── README.md              # Denne filen
```

### Feilsøking

#### "Ingen Twinkly enheter funnet"

- Sørg for at Twinkly Square er på samme nettverk som datamaskinen din
- Prøv å angi IP-adressen manuelt i `.env` filen
- Sjekk at Twinkly er slått på og koblet til WiFi

#### "Feil ved autentisering"

- Verifiser at Client ID og Client Secret er korrekt fra Netatmo Developer Portal
- Sjekk at brukernavnet (e-post) og passordet er riktig
- Sørg for at Netatmo-kontoen din har tilgang til værstasjonen

#### "Ingen temperaturdata funnet"

- Sjekk at værstasjonen er online i Netatmo-appen
- Verifiser at målemodulen sender data
- Prøv å logge inn på [https://my.netatmo.com](https://my.netatmo.com) for å se at data er tilgjengelig

#### Displayet viser ikke riktig

- Twinkly Square kan ha forskjellige størrelser (8x8, 10x10, 16x16)
- Koden antar 16x16, men kan justeres i `twinkly_client.py` hvis nødvendig

#### Services starter ikke automatisk

- Sjekk at stiene i `.service` filene er korrekte
- Verifiser at brukernavnet er riktig
- Kjør `sudo systemctl daemon-reload` etter endringer
- Sjekk loggene: `sudo journalctl -u twinkly-display.service -n 50`

### Tilpasninger

#### Endre oppdateringsintervall

Sett `UPDATE_SECONDS` i `.env` filen:
```env
UPDATE_SECONDS=30  # Oppdaterer hvert 30. sekund
```

#### Endre farger

I [twinkly_client.py](twinkly_client.py), metoden `show_temperature()`, kan du justere fargene:
```python
if temperature < 0:
    color = (0, 100, 255)  # RGB - juster verdier (0-255)
```

#### Vise andre data

Netatmo værstasjonen kan gi mer data (luftfuktighet, CO2, etc.). 
Se [netatmo_client.py](netatmo_client.py) for å hente andre verdier.

### Lisens

Dette er et personlig prosjekt for educational formål.

### Ressurser

- [Netatmo API Dokumentasjon](https://dev.netatmo.com/apidocumentation)
- [xled (Twinkly Python Library)](https://github.com/scrool/xled)
- [Twinkly Developer Portal](https://xled-docs.readthedocs.io/)
- [Yr API (MET Norway)](https://api.met.no/)
- [Hvakosterstrommen.no API](https://www.hvakosterstrommen.no/strompris-api)

---

## English

This project displays temperature from a Netatmo weather station, Yr outdoor temperature, and electricity prices on a Twinkly Square LED display.

### Features

- 🌡️ Fetches real-time temperature from Netatmo API
- ☀️ Fetches outdoor temperature from Yr (Sokndal, Norway)
- ⚡ Fetches electricity prices from Hvakosterstrommen.no (NO2 - Southern Norway)
- 💡 Displays temperature on Twinkly Square with color coding:
  - **Temperature:**
    - Blue: Below 0°C
    - Light blue: 0-10°C
    - Yellow: 10-20°C
    - Red/Orange: Above 20°C
  - **Electricity Price:**
    - Green: Below 50 øre/kWh
    - Yellow: 50-100 øre/kWh
    - Red: Above 100 øre/kWh
- 🎨 Unique icons for each location (Living Room, Kitchen, Basement, Attic, Outside, Electricity)
- 🔄 Automatic rotation between all locations
- 🕐 Digital clock with colors that change throughout the day
- �️ Weather animations based on Yr data:
  - ☀️ Sun: Pulsing sun with rays
  - 🌧️ Rain: Falling raindrops
  - ❄️ Snow: Drifting snowflakes
  - ⛈️ Thunder: Lightning bolts and white flashes
  - 🌫️ Fog: Moving fog banks
  - ⚡💰 Electricity warning: Blinking red screen when price exceeds 100 øre/kWh
- �🌐 Web interface on port 8080 for control and monitoring
- 🎨 Visual icon editor (24x16 grid) for creating and editing icons
- 🔐 OAuth2 authentication with automatic token refresh

### Prerequisites

- Python 3.7 or newer
- A Netatmo weather station with connected account
- A Twinkly Square LED display on the same network
- Netatmo Developer App (for API access)
- Git (for cloning the repository)
- Linux system with systemd (for automatic startup)

### Installation

#### 1. Clone repository

```bash
cd ~
git clone <repository-url> "Twinkly Square"
cd "Twinkly Square"
```

#### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set up Netatmo Developer App

1. Go to [Netatmo Developer Portal](https://dev.netatmo.com/)
2. Log in with your Netatmo account
3. Create a new app:
   - Click "Create" or "Create an app"
   - Fill in the required information (name, description, etc.)
   - After creation, note down:
     - **Client ID**
     - **Client Secret**

#### 5. Create configuration file

Create a `.env` file in the project folder:

```bash
nano .env
```

Fill in the following content:

```env
# Netatmo API credentials (from Developer Portal)
NETATMO_CLIENT_ID=your_client_id_here
NETATMO_CLIENT_SECRET=your_client_secret_here

# Your Netatmo username and password
NETATMO_USERNAME=your_email@example.com
NETATMO_PASSWORD=your_password

# Twinkly Square IP address (leave empty for auto-discovery)
TWINKLY_IP=

# Update interval in seconds (optional, default 60)
UPDATE_SECONDS=60
```

**Tips for finding Twinkly IP address:**
- Check your router for connected devices
- Use the Twinkly mobile app (check settings)
- Leave the field empty, and the script will try to find it automatically

#### 6. Test installation

Run the program manually to test:

```bash
python3 main.py
```

The program will:
1. Connect to Netatmo API and authenticate
2. Fetch outdoor temperature from Yr (Sokndal)
3. Fetch electricity price from Hvakosterstrommen.no (NO2)
4. Find and connect to Twinkly Square
5. Display temperatures and electricity price on the display
6. Rotate between all locations at the selected interval

Press `Ctrl+C` to stop.

#### 7. Set up systemd services (optional - for automatic startup)

Edit the service files to match your user and path:

```bash
# Edit display service
nano twinkly-display.service
# Change User=admog to your user
# Change WorkingDirectory to your path

# Edit web service
nano twinkly-web.service
# Change User=admog to your user
# Change WorkingDirectory to your path
```

Install and enable services:

```bash
# Copy service files
sudo cp twinkly-display.service /etc/systemd/system/
sudo cp twinkly-web.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services for automatic startup
sudo systemctl enable twinkly-display.service
sudo systemctl enable twinkly-web.service

# Start services
sudo systemctl start twinkly-display.service
sudo systemctl start twinkly-web.service

# Check status
sudo systemctl status twinkly-display.service
sudo systemctl status twinkly-web.service
```

### Usage

#### Manual execution

```bash
cd "Twinkly Square"
source .venv/bin/activate
python3 main.py
```

#### Web interface

Open a browser at `http://<your-ip>:8080` to:
- **View all temperatures and electricity price live** - Real-time data from all sensors
- **Switch between rotation and single display** - Automatically rotate between locations or choose a fixed view
- **Select specific location** - Display only one location (Living Room, Kitchen, Basement, Attic, Outside, or Electricity Price)
- **Adjust update interval** - Choose between 5-300 seconds for how often the display should update data
- **Toggle clock on/off** - Display a digital clock on the display with beautiful colors that change throughout the day
- **Start/stop the display** - Full control over the display state
- **Reconnect to Twinkly** - Manual reconnect button if Twinkly has been disconnected (e.g., after a power outage)

The web interface has a modern, responsive design that works on both desktop and mobile. All controls work in real-time without needing to restart the program.

**Automatic reconnect:** The program automatically attempts to connect to Twinkly at startup (10 attempts × 3s) and on connection failures during operation (5 attempts × 2s). If Twinkly has been disconnected for longer, you can use the reconnect button in the web interface.

#### Icon Editor

To create or edit icons, run the icon editor:

```bash
cd "Twinkly Square"
source .venv/bin/activate
python3 icon_editor.py
```

Open a browser at `http://<your-ip>:5000` to:
- **Draw icons** - Use a 24x16 grid to create pixel patterns
- **Load existing icons** - Edit icons that already exist
- **Save icons** - Saves directly to `icons.py` for immediate use
- **Delete icons** - Remove icons you don't need

The icon editor features:
- Click to draw, right-click or Shift+click to erase
- Drag with mouse to draw/erase multiple pixels
- Live preview of all icons
- Responsive design for desktop and mobile

#### Systemd service commands

```bash
# Start services
sudo systemctl start twinkly-display.service
sudo systemctl start twinkly-web.service

# Stop services
sudo systemctl stop twinkly-display.service
sudo systemctl stop twinkly-web.service

# Restart services
sudo systemctl restart twinkly-display.service
sudo systemctl restart twinkly-web.service

# Check status
sudo systemctl status twinkly-display.service
sudo systemctl status twinkly-web.service

# View logs
sudo journalctl -u twinkly-display.service -f
sudo journalctl -u twinkly-web.service -f
```

### Project Structure

```
.
├── main.py                 # Main program
├── netatmo_client.py       # Netatmo API client
├── yr_client.py            # Yr API client (MET Norway)
├── electricity_client.py   # Electricity price API client
├── twinkly_client.py       # Twinkly Square controller
├── icons.py                # Location icons
├── web_server.py           # Flask web server
├── icon_editor.py          # Visual icon editor
├── cleanup_display.py      # Cleanup script
├── templates/
│   ├── index.html         # Web interface
│   └── icon_editor.html   # Icon editor interface
├── requirements.txt        # Python dependencies
├── .env                    # Your configuration (do not commit!)
├── display_state.json      # State persistence (auto-generated)
├── twinkly-display.service # Systemd service (display)
├── twinkly-web.service     # Systemd service (web)
└── README.md              # This file
```

### Troubleshooting

#### "No Twinkly devices found"

- Ensure Twinkly Square is on the same network as your computer
- Try specifying the IP address manually in the `.env` file
- Check that Twinkly is powered on and connected to WiFi

#### "Authentication error"

- Verify that Client ID and Client Secret are correct from Netatmo Developer Portal
- Check that the username (email) and password are correct
- Ensure your Netatmo account has access to the weather station

#### "No temperature data found"

- Check that the weather station is online in the Netatmo app
- Verify that the measurement module is sending data
- Try logging in to [https://my.netatmo.com](https://my.netatmo.com) to see that data is available

#### Display not showing correctly

- Twinkly Square can have different sizes (8x8, 10x10, 16x16)
- The code assumes 16x16, but can be adjusted in `twinkly_client.py` if necessary

#### Services not starting automatically

- Check that the paths in the `.service` files are correct
- Verify that the username is correct
- Run `sudo systemctl daemon-reload` after changes
- Check the logs: `sudo journalctl -u twinkly-display.service -n 50`

### Customization

#### Change update interval

Set `UPDATE_SECONDS` in the `.env` file:
```env
UPDATE_SECONDS=30  # Updates every 30 seconds
```

#### Change colors

In [twinkly_client.py](twinkly_client.py), the `show_temperature()` method, you can adjust the colors:
```python
if temperature < 0:
    color = (0, 100, 255)  # RGB - adjust values (0-255)
```

#### Display other data

The Netatmo weather station can provide more data (humidity, CO2, etc.). 
See [netatmo_client.py](netatmo_client.py) to fetch other values.

### License

This is a personal project for educational purposes.

### Resources

- [Netatmo API Documentation](https://dev.netatmo.com/apidocumentation)
- [xled (Twinkly Python Library)](https://github.com/scrool/xled)
- [Twinkly Developer Portal](https://xled-docs.readthedocs.io/)
- [Yr API (MET Norway)](https://api.met.no/)
- [Hvakosterstrommen.no API](https://www.hvakosterstrommen.no/strompris-api)
