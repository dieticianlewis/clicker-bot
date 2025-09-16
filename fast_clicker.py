import time
import threading
from playwright.sync_api import sync_playwright, TimeoutError

# This script is aggressively optimized for maximum visits using parallel processing.
# It launches a separate thread for each platform, allowing all to run simultaneously.

# --- Configuration ---
URL = "https://sent.bio/alquis"

# --- IMPORTANT: TUNE THIS NUMBER ---
# Because we are running in parallel, we can now attempt a much higher number.
# Start with 60. If your workflow finishes in less than 50 seconds, increase it.
# If it takes more than 60 seconds, decrease it.
TOTAL_VISITS_PER_PLATFORM = 100

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

# --- NEW: This function contains the work that EACH thread will do ---
def run_platform_session(browser, platform_name, profile, num_visits):
    """
    This function is executed by a single thread. It performs all the visits
    for one specific platform.
    """
    print(f"--- Thread for {platform_name} started. Attempting {num_visits} visits. ---")
    
    for visit_num in range(1, num_visits + 1):
        page = None
        try:
            page = browser.new_page(
                user_agent=profile["user_agent"],
                viewport=profile["viewport"]
            )
            
            # Block unnecessary network resources
            page.route("**/*", lambda route: route.abort() if route.request.resource_type in BLOCKED_RESOURCE_TYPES else route.continue_())
            
            page.goto(URL, wait_until="domcontentloaded", timeout=20000)
            
            # The print statement is now inside the thread for clarity
            # print(f"  [{platform_name}] Visit {visit_num}/{num_visits} successful.")

        except Exception:
            # We can keep the output clean by not printing every single error in a high-frequency script
            # print(f"  [{platform_name}] FAILED visit {visit_num}.")
            pass
        finally:
            if page:
                page.close()
    
    print(f"--- Thread for {platform_name} finished. ---")


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Max-Performance PARALLEL Visitor ---")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        total_visits_to_perform = len(PLATFORM_PROFILES) * TOTAL_VISITS_PER_PLATFORM
        print(f"Browser launched. Will attempt {total_visits_to_perform} total visits across {len(PLATFORM_PROFILES)} threads.\n")

        threads = []
        # --- NEW: Loop to CREATE and START all the threads ---
        for platform, profile in PLATFORM_PROFILES.items():
            # Create a new thread object. Tell it which function to run (target)
            # and what arguments to give it (args).
            thread = threading.Thread(
                target=run_platform_session,
                args=(browser, platform, profile, TOTAL_VISITS_PER_PLATFORM)
            )
            threads.append(thread)
            # Start the thread. It will begin running in the background immediately.
            thread.start()

        # --- NEW: Loop to WAIT for all threads to finish ---
        # The main script will pause here until all the threads have completed.
        for thread in threads:
            thread.join()

        browser.close()
        print("\n--- All parallel visits complete. ---")