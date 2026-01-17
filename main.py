#!/usr/bin/env python3
"""
Netatmo til Twinkly Square Display
Viser temperatur fra Netatmo værstasjon på Twinkly Square
"""
import os
import time
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from netatmo_client import NetatmoClient
from twinkly_client import TwinklySquare
from yr_client import YrClient
from electricity_client import ElectricityClient


def get_state():
    """Hent nåværende state fra fil"""
    state_file = Path(__file__).parent / 'display_state.json'
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'mode': 'rotate',
        'location': None,
        'interval': int(os.getenv('UPDATE_SECONDS', 60)),
        'show_clock': False
    }


def reconnect_twinkly(twinkly, max_retries=5, retry_delay=2):
    """Prøv å koble til Twinkly på nytt med retry-logikk"""
    for attempt in range(1, max_retries + 1):
        if twinkly.connect() and twinkly.set_mode_rt():
            print(f"✓ Koblet til Twinkly på nytt (forsøk {attempt}/{max_retries})")
            return True
        if attempt < max_retries:
            print(f"  Reconnect forsøk {attempt}/{max_retries} feilet, prøver igjen om {retry_delay}s...")
            time.sleep(retry_delay)
    
    print(f"✗ Kunne ikke koble til Twinkly etter {max_retries} forsøk")
    return False


def main():
    """Hovedfunksjon"""
    print("=" * 50)
    print("Netatmo til Twinkly Square Display")
    print("=" * 50)
    
    # Last inn miljøvariabler fra .env fil
    load_dotenv()
    
    # Hent Netatmo credentials
    netatmo_client_id = os.getenv('NETATMO_CLIENT_ID')
    netatmo_client_secret = os.getenv('NETATMO_CLIENT_SECRET')
    netatmo_username = os.getenv('NETATMO_USERNAME')
    netatmo_password = os.getenv('NETATMO_PASSWORD')
    netatmo_refresh_token = os.getenv('NETATMO_REFRESH_TOKEN')
    
    # Hent Twinkly IP
    twinkly_ip = os.getenv('TWINKLY_IP')
    
    # Valider at alle nødvendige credentials er satt
    if not netatmo_client_id or not netatmo_client_secret:
        print("✗ Mangler Netatmo Client ID eller Client Secret!")
        print("Vennligst opprett en .env fil basert på .env.example")
        return
    
    if not netatmo_refresh_token and not (netatmo_username and netatmo_password):
        print("✗ Må ha enten NETATMO_REFRESH_TOKEN eller NETATMO_USERNAME/PASSWORD!")
        return
    
    print("\n1. Kobler til Netatmo...")
    netatmo = NetatmoClient(
        client_id=netatmo_client_id,
        client_secret=netatmo_client_secret,
        username=netatmo_username,
        password=netatmo_password,
        refresh_token=netatmo_refresh_token
    )
    
    print("\n2. Kobler til Twinkly Square...")
    twinkly = TwinklySquare(ip_address=twinkly_ip)
    
    # Prøv å koble til med retry - Twinkly kan ta tid å starte opp
    max_retries = 10
    retry_delay = 3
    connected = False
    
    for attempt in range(1, max_retries + 1):
        if twinkly.connect():
            connected = True
            print(f"✓ Koblet til Twinkly (forsøk {attempt}/{max_retries})")
            break
        else:
            if attempt < max_retries:
                print(f"  Kunne ikke koble til Twinkly (forsøk {attempt}/{max_retries}), prøver igjen om {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"✗ Kunne ikke koble til Twinkly etter {max_retries} forsøk")
    
    if not connected:
        print("✗ Kunne ikke koble til Twinkly Square")
        return
    
    if not twinkly.set_mode_rt():
        print("✗ Kunne ikke sette Twinkly til realtime modus")
        return
    
    # Initialiser Yr og Strømpris klienter
    print("\n2b. Initialiserer Yr og Strømpris...")
    yr_client = YrClient(lat=58.35, lon=6.63)  # Sokndal
    electricity_client = ElectricityClient(region='NO2')  # Sør-Norge
    
    # Hent alle tilgjengelige temperaturer
    print("\n3. Henter tilgjengelige moduler...")
    all_temps = netatmo.get_all_temperatures()
    
    if not all_temps:
        print("✗ Kunne ikke hente noen temperaturdata")
        return
    
    # Legg til Yr og Strømpris
    yr_temp = yr_client.get_current_temperature()
    if yr_temp is not None:
        all_temps['Ute (Sokndal)'] = yr_temp
        print(f"✓ Yr utetemperatur: {yr_temp}°C")
    
    electricity_price = electricity_client.get_current_price()
    if electricity_price is not None:
        all_temps['Strømpris NO2'] = electricity_price
        print(f"✓ Strømpris: {electricity_price} øre/kWh")
    
    locations = list(all_temps.keys())
    print(f"✓ Fant {len(locations)} lokasjoner: {', '.join(locations)}")

    
    # Hent state fra fil
    state = get_state()
    update_interval = state.get('interval', 60)
    display_mode = state.get('mode', 'single')
    single_location = state.get('location')
    show_clock = state.get('show_clock', False)
    
    if show_clock:
        print(f"\n4. Starter klokke-visning...")
        print(f"(Oppdaterer hvert sekund. Trykk Ctrl+C for å stoppe)\n")
    elif display_mode == 'single' and single_location:
        print(f"\n4. Starter visning av {single_location}...")
        print(f"(Oppdaterer hvert {update_interval} sekund. Trykk Ctrl+C for å stoppe)\n")
    else:
        print(f"\n4. Starter visning av temperatur...")
        print(f"(Roterer mellom lokasjoner hvert {update_interval} sekund. Trykk Ctrl+C for å stoppe)\n")
    
    location_index = 0
    last_rt_reset = time.time()
    last_mode = display_mode
    last_location = single_location
    last_clock_state = show_clock
    first_run = True
    
    try:
        while True:
            # Resett realtime modus hvert 30. sekund for å holde den aktiv
            current_time = time.time()
            if current_time - last_rt_reset >= 30:
                print("  [Resetter realtime-modus]")
                twinkly.set_mode_rt()
                last_rt_reset = current_time
            
            # Les state på nytt for å få oppdateringer
            state = get_state()
            update_interval = state.get('interval', 10)
            display_mode = state.get('mode', 'single')
            single_location = state.get('location')
            show_clock = state.get('show_clock', False)
            
            # Sjekk om mode eller location har endret seg
            mode_changed = (display_mode != last_mode or single_location != last_location or show_clock != last_clock_state)
            last_mode = display_mode
            last_location = single_location
            last_clock_state = show_clock
            
            # Hvis klokke er aktivert, vis klokke
            if show_clock:
                now = datetime.now()
                if twinkly.show_clock(now.hour, now.minute):
                    if first_run or mode_changed:
                        print(f"✓ Viser klokke: {now.hour:02d}:{now.minute:02d}")
                        first_run = False
                else:
                    print("✗ Kunne ikke oppdatere Twinkly display - prøver å koble til på nytt...")
                    if not reconnect_twinkly(twinkly):
                        print("⚠ Kunne ikke gjenopprette tilkobling, venter...")
                        time.sleep(10)
                
                # Oppdater klokken hvert sekund
                time.sleep(1)
                continue
            
            # Hent alle temperaturer
            all_temps = netatmo.get_all_temperatures()
            
            # Legg til Yr og Strømpris
            yr_temp = yr_client.get_current_temperature()
            yr_weather = yr_client.get_weather_data()
            
            if yr_temp is not None:
                all_temps['Ute (Sokndal)'] = yr_temp
            
            electricity_price = electricity_client.get_current_price()
            if electricity_price is not None:
                all_temps['Strømpris NO2'] = electricity_price
            
            # Vis væranimajoner og strømpris-varsling
            show_animations = False  # Vis animasjoner hver 5. iterasjon
            if location_index % 5 == 0:
                show_animations = True
            
            if show_animations:
                # Vis strømpris-varsling hvis pris er høy (over 100 øre)
                if electricity_price and electricity_price > 100:
                    print(f"⚡ Strømpris-varsling: {electricity_price} øre/kWh")
                    twinkly.show_electricity_warning(electricity_price, threshold=100, duration=2)
                
                # Vis væranimasjon basert på værsymbol
                if yr_weather and yr_weather.get('symbol'):
                    symbol = yr_weather['symbol']
                    if 'rain' in symbol or 'drizzle' in symbol:
                        print("🌧️ Viser regn-animasjon")
                        twinkly.show_rain_animation(duration=2)
                    elif 'snow' in symbol or 'sleet' in symbol:
                        print("❄️ Viser snø-animasjon")
                        twinkly.show_snow_animation(duration=2)
                    elif 'clearsky' in symbol or 'fair' in symbol:
                        print("☀️ Viser sol-animasjon")
                        twinkly.show_sun_animation(duration=2)

            
            if all_temps:
                # Oppdater locations liste
                locations = list(all_temps.keys())
                
                if display_mode == 'single' and single_location:
                    # Vis kun én lokasjon - sjekk om lokasjon finnes
                    if single_location in all_temps:
                        temperature = all_temps[single_location]
                        if twinkly.show_temperature_with_icon(temperature, single_location):
                            print(f"✓ Viser {single_location}: {temperature}°C")
                        else:
                            print("✗ Kunne ikke oppdatere Twinkly display - prøver å koble til på nytt...")
                            if not reconnect_twinkly(twinkly):
                                print("⚠ Kunne ikke gjenopprette tilkobling, venter...")
                                time.sleep(10)
                    else:
                        print(f"✗ Lokasjon {single_location} ikke funnet")
                    
                    # Hvis mode/location endret eller første kjøring, ikke vent - vis umiddelbart
                    if mode_changed or first_run:
                        if mode_changed:
                            print(f"  [Byttet til single mode: {single_location}]")
                        first_run = False
                        time.sleep(1)  # Kort pause for å unngå spam
                        continue  # Gå til neste iterasjon uten å vente
                        
                else:
                    # Roter mellom lokasjoner (default eller når mode == 'rotate')
                    if locations:
                        current_location = locations[location_index]
                        
                        if current_location in all_temps:
                            temperature = all_temps[current_location]
                            
                            # Vis temperaturen med ikon på Twinkly Square
                            if twinkly.show_temperature_with_icon(temperature, current_location):
                                print(f"✓ Viser {current_location}: {temperature}°C")
                            else:
                                print("✗ Kunne ikke oppdatere Twinkly display - prøver å koble til på nytt...")
                                if not reconnect_twinkly(twinkly):
                                    print("⚠ Kunne ikke gjenopprette tilkobling, venter...")
                                    time.sleep(10)
                        else:
                            print(f"✗ Kunne ikke hente temperatur fra {current_location}")
                        
                        # Hvis mode endret til rotate eller første kjøring, ikke vent - start rotasjon umiddelbart
                        if mode_changed or first_run:
                            if mode_changed:
                                print(f"  [Byttet til rotate mode]")
                            first_run = False
                            time.sleep(1)  # Kort pause
                            continue  # Gå til neste iterasjon uten å vente
                        
                        # Gå til neste lokasjon
                        location_index = (location_index + 1) % len(locations)
            else:
                print("✗ Kunne ikke hente temperaturdata")
            
            # Vent før neste oppdatering
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print("\n\nStopper...")
        twinkly.clear()
        print("✓ Display slettet")
    except Exception as e:
        print(f"\n✗ Uventet feil: {e}")
        twinkly.clear()


if __name__ == "__main__":
    main()
