#!/usr/bin/env python3
"""
Debug script for å se LED koordinater
"""
import os
from dotenv import load_dotenv
from xled.control import HighControlInterface


def check_coordinates():
    load_dotenv()
    twinkly_ip = os.getenv('TWINKLY_IP')
    
    print(f"Kobler til Twinkly på {twinkly_ip}...")
    control = HighControlInterface(twinkly_ip)
    
    layout = control.get_led_layout()
    coords = layout['coordinates']
    
    print(f"\nTotalt {len(coords)} LEDs")
    print("\nFørste 10 koordinater:")
    for i in range(min(10, len(coords))):
        print(f"  LED {i}: x={coords[i]['x']:.4f}, y={coords[i]['y']:.4f}")
    
    # Finn min/max verdier
    x_values = [c['x'] for c in coords]
    y_values = [c['y'] for c in coords]
    
    print(f"\nX-verdier: min={min(x_values):.4f}, max={max(x_values):.4f}")
    print(f"Y-verdier: min={min(y_values):.4f}, max={max(y_values):.4f}")
    
    # Tell hvor mange LEDs er i forskjellige områder
    print("\nFordeling av LEDs:")
    x_bins = [0, 0.333, 0.667, 1.0]
    y_bins = [0, 0.5, 1.0]
    
    for yi in range(len(y_bins)-1):
        for xi in range(len(x_bins)-1):
            count = sum(1 for c in coords 
                       if x_bins[xi] <= c['x'] < x_bins[xi+1] 
                       and y_bins[yi] <= c['y'] < y_bins[yi+1])
            print(f"  x=[{x_bins[xi]:.2f}-{x_bins[xi+1]:.2f}], y=[{y_bins[yi]:.2f}-{y_bins[yi+1]:.2f}]: {count} LEDs")


if __name__ == "__main__":
    check_coordinates()
