#!/usr/bin/env python3
"""
Enklere test - viser bare ÉN panel om gangen med full farge
"""
import os
import time
from dotenv import load_dotenv
from twinkly_client import TwinklySquare


def test_single_panels():
    """Test hvert panel individuelt med full farge"""
    print("=" * 50)
    print("Twinkly Enkel Panel Test")
    print("=" * 50)
    
    load_dotenv()
    twinkly_ip = os.getenv('TWINKLY_IP')
    
    print("\nKobler til Twinkly...")
    twinkly = TwinklySquare(ip_address=twinkly_ip)
    
    if not twinkly.connect():
        print("✗ Kunne ikke koble til Twinkly")
        return
    
    if not twinkly.set_mode_rt():
        print("✗ Kunne ikke sette realtime modus")
        return
    
    # Definer 6 panel-områder (8x8 hver)
    # Layout: 3 bredt x 2 høyt
    panel_areas = [
        {"navn": "Område 1 (Øvre Venstre)", "x_start": 0, "x_end": 8, "y_start": 0, "y_end": 8},
        {"navn": "Område 2 (Øvre Midten)", "x_start": 8, "x_end": 16, "y_start": 0, "y_end": 8},
        {"navn": "Område 3 (Øvre Høyre)", "x_start": 16, "x_end": 24, "y_start": 0, "y_end": 8},
        {"navn": "Område 4 (Nedre Venstre)", "x_start": 0, "x_end": 8, "y_start": 8, "y_end": 16},
        {"navn": "Område 5 (Nedre Midten)", "x_start": 8, "x_end": 16, "y_start": 8, "y_end": 16},
        {"navn": "Område 6 (Nedre Høyre)", "x_start": 16, "x_end": 24, "y_start": 8, "y_end": 16},
    ]
    
    colors = [
        (255, 0, 0),    # Rød
        (0, 255, 0),    # Grønn
        (0, 0, 255),    # Blå
        (255, 255, 0),  # Gul
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
    ]
    
    print("\n" + "=" * 50)
    print("Viser hvert område i en egen farge")
    print("=" * 50)
    
    results = []
    
    try:
        for i, (area, color) in enumerate(zip(panel_areas, colors), 1):
            # Lag tomt canvas
            canvas = [[(0, 0, 0) for _ in range(24)] for _ in range(16)]
            
            # Fyll hele området med fargen
            for y in range(area["y_start"], area["y_end"]):
                for x in range(area["x_start"], area["x_end"]):
                    canvas[y][x] = color
            
            color_name = ["Rød", "Grønn", "Blå", "Gul", "Magenta", "Cyan"][i-1]
            
            print(f"\n{'='*50}")
            print(f"Område {i}: {area['navn']}")
            print(f"Farge: {color_name}")
            print(f"{'='*50}")
            
            twinkly.show_pattern(canvas)
            
            print("\nHvilket panel i ditt oppsett lyser nå?")
            print("  Svar: øvre venstre / øvre midten / øvre høyre")
            print("        nedre venstre / nedre midten / nedre høyre")
            print("        ingen / kontrollpanel")
            panel_pos = input("  >> ").strip()
            
            results.append({
                "område": area["navn"],
                "farge": color_name,
                "faktisk_panel": panel_pos
            })
            
            time.sleep(0.5)
        
        # Sammendrag
        print("\n" + "=" * 50)
        print("PANEL-MAPPING RESULTAT:")
        print("=" * 50)
        for r in results:
            print(f"{r['område']} ({r['farge']})")
            print(f"  -> Faktisk panel: {r['faktisk_panel']}")
            print()
        
    except KeyboardInterrupt:
        print("\n\nAvbrutt")
    finally:
        print("Renser display...")
        twinkly.clear()
        print("✓ Ferdig!")


if __name__ == "__main__":
    test_single_panels()
