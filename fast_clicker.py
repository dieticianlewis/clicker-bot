import time
from playwright.sync_api import sync_playwright, TimeoutError

# This script uses Playwright to visit a URL from multiple device/OS perspectives.
# It is designed to be as fast as possible by reusing a single browser instance.
# It clicks on a predefined list of mouse coordinates, which is necessary for
# frameworks like Flutter where traditional link selectors do not work.

# --- Configuration ---
URL = "https://sent.bio/alquis"

# --- IMPORTANT: DEFINE YOUR CLICK COORDINATES HERE ---
# Use a tool (like a screenshot editor) to find the X and Y coordinates
# of the elements you want to click on the page.
CLICK_COORDINATES = [
    {"name": "Twitter Link", "x": 750, "y": 250},
    {"name": "Instagram Link", "x": 800, "y": 250},
    {"name": "Another Button", "x": 600, "y": 400},
    # Add as many links/buttons as you need
]

# A dictionary of User-Agent strings for the platforms you want to simulate.
USER_AGENTS = {
    "Windows 10 (Chrome)": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    "macOS (Safari)": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Linux (Firefox)": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "iOS (iPhone/Safari)": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
    "Android (Chrome Mobile)": "Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36",
    "Chrome OS (Chromebook)": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.59 Safari/537.36"
}

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting High-Speed Visitor and Clicker ---")
    
    with sync_playwright() as p:
        # For maximum speed, we launch the browser only ONCE.
        browser = p.chromium.launch(headless=True)
        print(f"Browser launched. Will now cycle through {len(USER_AGENTS)} different platforms.\n")

        for platform, user_agent in USER_AGENTS.items():
            print(f"--- Visiting as: {platform} ---")
            
            # Create a new, isolated page with the specified User-Agent.
            page = browser.new_page(user_agent=user_agent)
            
            try:
                # 1. Navigate to the page.
                print(f"  Navigating to {URL}...")
                page.goto(URL, wait_until="load", timeout=30000)

                # 2. Wait for the core Flutter application to render. This is crucial.
                print("  Waiting for Flutter application to attach...")
                page.locator("flutter-view").wait_for(state='attached', timeout=20000)
                print("  Application loaded.")

                # 3. Loop through and click on the specified coordinates.
                for click_target in CLICK_COORDINATES:
                    name = click_target["name"]
                    x_coord = click_target["x"]
                    y_coord = click_target["y"]
                    
                    print(f"  Clicking on '{name}' at coordinates (X:{x_coord}, Y:{y_coord})...")
                    
                    # This is a "fire-and-forget" click. It performs the action
                    # without waiting for a new page to load, making it very fast.
                    page.mouse.click(x_coord, y_coord)
                    
                    # A tiny pause to allow the page to react if needed.
                    page.wait_for_timeout(500)

            except TimeoutError as e:
                print(f"  FAILED: A timeout occurred while loading the page: {e}")
            except Exception as e:
                print(f"  FAILED: An unexpected error occurred: {e}")
            finally:
                # Close the page to free up memory for the next run.
                page.close()
                print("  Session for this platform complete.\n")

        # After the loop is finished, close the browser.
        browser.close()
        print("--- All visits complete. ---")