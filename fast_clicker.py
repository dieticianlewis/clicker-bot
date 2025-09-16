import time
import re
from playwright.sync_api import sync_playwright, TimeoutError

# This script is aggressively optimized for maximum visits within a short time frame.
# It achieves this by blocking non-essential resources like images, CSS, and fonts.

# --- Configuration ---
URL = "https://sent.bio/alquis"

# --- IMPORTANT: TUNE THIS NUMBER ---
# This is the target number of visits for EACH platform.
# Start with 20. If your workflow finishes in less than 50 seconds, increase it.
# If it takes more than 60 seconds, decrease it.
TOTAL_VISITS_PER_PLATFORM = 50

# A list of resource types to block to speed up page loading.
BLOCKED_RESOURCE_TYPES = [
  "image",
  "stylesheet",
  "font",
  "media",
  "other",
]

# A focused dictionary of the 6 platforms you requested.
PLATFORM_PROFILES = {
    "Windows (Chrome)": {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", "viewport": {"width": 1920, "height": 1080}},
    "macOS (Safari)": {"user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15", "viewport": {"width": 1920, "height": 1080}},
    "Linux (Firefox)": {"user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0", "viewport": {"width": 1920, "height": 1080}},
    "iOS (iPhone)": {"user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1", "viewport": {"width": 390, "height": 844}},
    "Android (Samsung)": {"user_agent": "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36", "viewport": {"width": 412, "height": 915}},
    "Chrome OS (Chromebook)": {"user_agent": "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.59 Safari/537.36", "viewport": {"width": 1280, "height": 800}}
}

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Max-Performance Visitor ---")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        total_visits_to_perform = len(PLATFORM_PROFILES) * TOTAL_VISITS_PER_PLATFORM
        print(f"Browser launched. Will attempt {total_visits_to_perform} total visits.\n")

        for platform, profile in PLATFORM_PROFILES.items():
            print(f"--- Starting session for: {platform} ---")
            
            for visit_num in range(1, TOTAL_VISITS_PER_PLATFORM + 1):
                page = None
                try:
                    page = browser.new_page(
                        user_agent=profile["user_agent"],
                        viewport=profile["viewport"]
                    )
                    
                    # --- OPTIMIZATION: Block unnecessary network resources ---
                    page.route("**/*", lambda route: route.abort() if route.request.resource_type in BLOCKED_RESOURCE_TYPES else route.continue_())
                    
                    # Navigate to the page
                    page.goto(URL, wait_until="domcontentloaded", timeout=20000)

                    # We don't need to wait for the flutter-view, as the visit is
                    # registered as soon as the main HTML content is loaded.
                    
                    print(f"  Visit {visit_num}/{TOTAL_VISITS_PER_PLATFORM} successful.")

                except TimeoutError:
                    print(f"  FAILED visit {visit_num}: A timeout occurred.")
                except Exception as e:
                    print(f"  FAILED visit {visit_num}: An unexpected error occurred: {e}")
                finally:
                    if page:
                        page.close()
            
            print(f"--- Session for {platform} complete. ---\n")

        browser.close()
        print("--- All visits complete. ---")