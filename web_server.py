#!/usr/bin/env python3
"""
Webserver for å kontrollere Twinkly Display
"""
from flask import Flask, render_template, jsonify, request
import subprocess
import json
import os
from pathlib import Path
from dotenv import load_dotenv

app = Flask(__name__)

# Last miljøvariabler
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# State fil for å lagre innstillinger
STATE_FILE = Path(__file__).parent / 'display_state.json'

def get_state():
    """Hent nåværende state"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        'mode': 'single',  # 'rotate' eller 'single' - standard single
        'location': 'Stue - 70:ee:50:74:46:9c',  # Standard lokasjon
        'interval': 10,  # Standard 10 sekunder
        'service_running': is_service_running(),
        'show_clock': False
    }

def save_state(state):
    """Lagre state til fil"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def is_service_running():
    """Sjekk om main.py kjører"""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'python.*main.py'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def get_locations():
    """Hent liste over tilgjengelige lokasjoner"""
    try:
        # Importer alle klienter
        from netatmo_client import NetatmoClient
        from yr_client import YrClient
        from electricity_client import ElectricityClient
        
        locations = []
        
        # Hent Netatmo lokasjoner
        netatmo_client_id = os.getenv('NETATMO_CLIENT_ID')
        netatmo_client_secret = os.getenv('NETATMO_CLIENT_SECRET')
        netatmo_refresh_token = os.getenv('NETATMO_REFRESH_TOKEN')
        netatmo_username = os.getenv('NETATMO_USERNAME')
        netatmo_password = os.getenv('NETATMO_PASSWORD')
        
        if netatmo_client_id and netatmo_client_secret:
            netatmo = NetatmoClient(
                client_id=netatmo_client_id,
                client_secret=netatmo_client_secret,
                username=netatmo_username,
                password=netatmo_password,
                refresh_token=netatmo_refresh_token
            )
            temps = netatmo.get_all_temperatures()
            locations.extend(list(temps.keys()))
        
        # Legg til Yr og Strømpris
        locations.append('Ute (Sokndal)')
        locations.append('Strømpris NO2')
        
        return locations
    except Exception as e:
        print(f"Feil ved henting av lokasjoner: {e}")
        return []

@app.route('/')
def index():
    """Vis kontrollpanel"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Hent status"""
    state = get_state()
    state['service_running'] = is_service_running()
    state['locations'] = get_locations()
    
    # Hent temperaturer
    try:
        from netatmo_client import NetatmoClient
        from yr_client import YrClient
        from electricity_client import ElectricityClient
        
        netatmo_client_id = os.getenv('NETATMO_CLIENT_ID')
        netatmo_client_secret = os.getenv('NETATMO_CLIENT_SECRET')
        netatmo_refresh_token = os.getenv('NETATMO_REFRESH_TOKEN')
        netatmo_username = os.getenv('NETATMO_USERNAME')
        netatmo_password = os.getenv('NETATMO_PASSWORD')
        
        temperatures = {}
        
        if netatmo_client_id and netatmo_client_secret:
            netatmo = NetatmoClient(
                client_id=netatmo_client_id,
                client_secret=netatmo_client_secret,
                username=netatmo_username,
                password=netatmo_password,
                refresh_token=netatmo_refresh_token
            )
            temperatures = netatmo.get_all_temperatures()
        
        # Legg til Yr utetemperatur
        try:
            yr = YrClient(lat=58.35, lon=6.63)
            yr_temp = yr.get_current_temperature()
            if yr_temp is not None:
                temperatures['Ute (Sokndal)'] = yr_temp
        except Exception as e:
            print(f"Yr feil: {e}")
        
        # Legg til strømpris
        try:
            electricity = ElectricityClient(region='NO2')
            price = electricity.get_current_price()
            if price is not None:
                temperatures['Strømpris NO2'] = price
        except Exception as e:
            print(f"Strømpris feil: {e}")
        
        state['temperatures'] = temperatures
        
    except Exception as e:
        print(f"Feil ved henting av temperaturer: {e}")
        state['temperatures'] = {}
    
    return jsonify(state)

@app.route('/api/start', methods=['POST'])
def start_service():
    """Start display service"""
    try:
        # Stopp først hvis den kjører
        subprocess.run(['pkill', '-f', 'python.*main.py'], capture_output=True)
        
        import time
        time.sleep(0.5)
        
        # Start på nytt med riktig env
        venv_python = str(Path(__file__).parent / '.venv' / 'bin' / 'python')
        main_script = str(Path(__file__).parent / 'main.py')
        work_dir = str(Path(__file__).parent)
        
        subprocess.Popen(
            [venv_python, main_script],
            cwd=work_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=os.environ.copy()
        )
        
        state = get_state()
        state['service_running'] = True
        save_state(state)
        
        return jsonify({'success': True, 'message': 'Service startet'})
    except Exception as e:
        print(f"Feil i start_service: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_service():
    """Stopp display service og slå av Twinkly"""
    try:
        # Stopp main.py prosessen
        subprocess.run(['pkill', '-f', 'python.*main.py'], capture_output=True)
        
        # Slå av Twinkly display
        try:
            from twinkly_client import TwinklySquare
            twinkly_ip = os.getenv('TWINKLY_IP')
            if twinkly_ip:
                twinkly = TwinklySquare(ip_address=twinkly_ip)
                if twinkly.connect():
                    twinkly.clear()
                    print("✓ Twinkly display slått av")
        except Exception as e:
            print(f"Kunne ikke slå av Twinkly: {e}")
        
        state = get_state()
        state['service_running'] = False
        save_state(state)
        
        return jsonify({'success': True, 'message': 'Service stoppet og display slått av'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Sett modus (rotate eller single)"""
    try:
        data = request.json
        mode = data.get('mode')
        
        if mode not in ['rotate', 'single']:
            return jsonify({'success': False, 'error': 'Ugyldig modus'}), 400
        
        state = get_state()
        state['mode'] = mode
        state['show_clock'] = False  # Skru av klokke når mode endres
        
        if mode == 'single':
            location = data.get('location')
            if not location:
                return jsonify({'success': False, 'error': 'Location kreves for single mode'}), 400
            state['location'] = location
        else:
            state['location'] = None
        
        save_state(state)
        
        # Restart service hvis den kjører
        if is_service_running():
            subprocess.run(['pkill', '-f', 'python.*main.py'], capture_output=True)
            import time
            time.sleep(0.5)
            
            venv_python = str(Path(__file__).parent / '.venv' / 'bin' / 'python')
            main_script = str(Path(__file__).parent / 'main.py')
            work_dir = str(Path(__file__).parent)
            
            subprocess.Popen(
                [venv_python, main_script],
                cwd=work_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=os.environ.copy()
            )
        
        return jsonify({'success': True, 'message': 'Modus oppdatert'})
    except Exception as e:
        print(f"Feil i set_mode: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interval', methods=['POST'])
def set_interval():
    """Sett oppdateringsintervall"""
    try:
        data = request.json
        interval = data.get('interval')
        
        if not interval or not isinstance(interval, int) or interval < 5:
            return jsonify({'success': False, 'error': 'Intervall må være minst 5 sekunder'}), 400
        
        state = get_state()
        state['interval'] = interval
        save_state(state)
        
        # Restart service hvis den kjører (main.py leser state-filen)
        if is_service_running():
            subprocess.run(['pkill', '-f', 'python.*main.py'], capture_output=True)
            import time
            time.sleep(0.5)
            
            venv_python = str(Path(__file__).parent / '.venv' / 'bin' / 'python')
            main_script = str(Path(__file__).parent / 'main.py')
            work_dir = str(Path(__file__).parent)
            
            subprocess.Popen(
                [venv_python, main_script],
                cwd=work_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=os.environ.copy()
            )
        
        return jsonify({'success': True, 'message': f'Intervall satt til {interval} sekunder'})
    except Exception as e:
        print(f"Feil i set_interval: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clock', methods=['POST'])
def toggle_clock():
    """Skru klokke av eller på"""
    try:
        data = request.json
        show_clock = data.get('show_clock', False)
        
        state = get_state()
        state['show_clock'] = show_clock
        save_state(state)
        
        # Restart service hvis den kjører
        if is_service_running():
            subprocess.run(['pkill', '-f', 'python.*main.py'], capture_output=True)
            import time
            time.sleep(0.5)
            
            venv_python = str(Path(__file__).parent / '.venv' / 'bin' / 'python')
            main_script = str(Path(__file__).parent / 'main.py')
            work_dir = str(Path(__file__).parent)
            
            subprocess.Popen(
                [venv_python, main_script],
                cwd=work_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=os.environ.copy()
            )
        
        message = 'Klokke aktivert' if show_clock else 'Klokke deaktivert'
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        print(f"Feil i toggle_clock: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reconnect', methods=['POST'])
def reconnect_twinkly():
    """Prøv å koble til Twinkly på nytt"""
    try:
        from twinkly_client import TwinklySquare
        twinkly_ip = os.getenv('TWINKLY_IP')
        
        if not twinkly_ip:
            return jsonify({'success': False, 'error': 'Twinkly IP ikke konfigurert'}), 400
        
        # Prøv å koble til
        twinkly = TwinklySquare(ip_address=twinkly_ip)
        
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            if twinkly.connect():
                if twinkly.set_mode_rt():
                    return jsonify({
                        'success': True, 
                        'message': f'✓ Koblet til Twinkly (forsøk {attempt}/{max_retries})'
                    })
            
            if attempt < max_retries:
                import time
                time.sleep(2)
        
        return jsonify({
            'success': False, 
            'error': f'Kunne ikke koble til Twinkly etter {max_retries} forsøk'
        }), 500
        
    except Exception as e:
        print(f"Feil i reconnect_twinkly: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Opprett templates mappe hvis den ikke finnes
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    app.run(host='0.0.0.0', port=8080, debug=False)
