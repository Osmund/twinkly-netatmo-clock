#!/usr/bin/env python3
"""
Cleanup script - slår av Twinkly display
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from twinkly_client import TwinklySquare

# Last miljøvariabler
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def cleanup():
    """Slå av Twinkly display"""
    try:
        twinkly_ip = os.getenv('TWINKLY_IP')
        if twinkly_ip:
            twinkly = TwinklySquare(ip_address=twinkly_ip)
            if twinkly.connect():
                twinkly.clear()
                print("✓ Twinkly display slått av")
                return True
        print("⚠ Kunne ikke finne Twinkly IP")
        return False
    except Exception as e:
        print(f"✗ Feil ved sletting av display: {e}")
        return False

if __name__ == "__main__":
    cleanup()
