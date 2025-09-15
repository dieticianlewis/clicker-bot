import time
import random
from playwright.sync_api import sync_playwright, TimeoutError

# This script uses specific, different coordinate sets for desktop and mobile
# platforms, ensuring clicks are accurate for each layout.

# --- Configuration ---
URL = "https://sent.bio/alquis"

# --- IMPORTANT: FINAL COORDINATES ---

# 1. Coordinates for your 1920x1080 desktop screen
DESKTOP_CLICK_COORDINATES = [
    {"name": "First Link (Desktop)", "x": 956, "y": 415},
    {"name": "Second Link (Desktop)", "x": 955, "y": 515},
    {"name": "Third Link (Desktop)", "x": 952, "y": 607},
]

# 2. Coordinates for mobile screens (Calculated from your Samsung data)
MOBILE_CLICK_COORDINATES = [
    {"name": "First Link (Mobile)", "x": 183, "y": 378},
    {"name": "Second Link (Mobile)", "x": 183, "y": 468},
    {"name": "Third Link (Mobile)", "x": 183, "y": 558},
]

# A focused dictionary of the 6 platforms you requested.
PLATFORM_PROFILES = {
    # Desktop platforms will use DESKTOP_CLICK_COORDINATES
    "Windows (Chrome)": {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", "viewport": {"width": 1920, "height": 1080}},
    "macOS (Safari)": {"user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15", "viewport": {"width": 1920, "height": 1080}},
    "Linux (Firefox)": {"user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0", "viewport": {"width": 1920, "height": 1080}},
    "Chrome OS (Chromebook)": {"user_agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.59 Safari/537.36", "viewport": {"width": 1280, "height": 800}},
    # Mobile platforms will use MOBILE_CLICK_COORDINATES
    "iOS (iPhone)": {"user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1", "viewport": {"width": 390, "height": 844}},
    "Android (Samsung)": {"user_agent": "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36", "viewport": {"width": 412, "height": 915}}
}

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Smart Visitor and Clicker ---")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        print(f"Browser launched. Will now visit on {len(PLATFORM_PROFILES)} specified platforms.\n")

        for platform, profile in PLATFORM_PROFILES.items():
            print(f"--- Visiting as: {platform} ---")
            
            page = browser.new_page(
                user_agent=profile["user_agent"],
                viewport=profile["viewport"]
            )
            
            try:
                print(f"  Navigating to {URL} with viewport {profile['viewport']}...")
                page.goto(URL, wait_until="domcontentloaded", timeout=30000)
                print("  Waiting for Flutter application to attach...")
                page.locator("flutter-view").wait_for(state='attached', timeout=20000)
                print("  Application loaded.")

                # Scroll down to make the links visible
                print("  Scrolling down...")
                page.mouse.wheel(0, 1500)
                page.wait_for_timeout(1000)

                # Choose the correct coordinate list based on screen width
                is_desktop = profile['viewport']['width'] > 800
                click_list = DESKTOP_CLICK_COORDINATES if is_desktop else MOBILE_CLICK_COORDINATES
                
                print(f"  Using {'Desktop' if is_desktop else 'Mobile'} coordinates.")

                for click_target in click_list:
                    name = click_target["name"]
                    # Add a small, random offset to make the click more human
                    offset_x = random.randint(-2, 2)
                    offset_y = random.randint(-2, 2)
                    x_coord = click_target["x"] + offset_x
                    y_coord = click_target["y"] + offset_y
                    
                    print(f"  Clicking '{name}' at randomized coordinates (X:{x_coord}, Y:{y_coord})...")
                    page.mouse.click(x_coord, y_coord)
                    page.wait_for_timeout(500)

            except TimeoutError as e:
                print(f"  FAILED: A timeout occurred: {e}")
            except Exception as e:
                print(f"  FAILED: An unexpected error occurred: {e}")
            finally:
                page.close()
                print("  Session for this platform complete.\n")

        browser.close()
        print("--- All visits complete. ---")