import threading
from playwright.sync_api import sync_playwright

# This is the most optimized version of the parallel script. It uses page reloading
# and context-level routing to minimize overhead inside each thread, maximizing
# the number of visits possible in a short time.

# --- Configuration ---
URL = "https://sent.bio/alquis"

# --- IMPORTANT: TUNE THIS NUMBER ---
# With these new optimizations, you can likely increase this number.
# Try starting with 220 or 250 and adjust based on your workflow's run time.
TOTAL_VISITS_PER_PLATFORM = 220

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

# --- This function contains the ENTIRE lifecycle for a single thread ---
def run_platform_session(platform_name, profile, num_visits):
    """
    Executed by a single thread. It starts its own Playwright instance,
    browser, and performs all visits by reloading a single page.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=profile["user_agent"],
                viewport=profile["viewport"]
            )
            
            # --- OPTIMIZATION 1: Set routing rules ONCE per thread ---
            context.route("**/*", lambda route: route.abort() if route.request.resource_type in BLOCKED_RESOURCE_TYPES else route.continue_())
            
            page = context.new_page()
            
            print(f"--- Thread for {platform_name} started. Attempting {num_visits} visits. ---")

            # First visit uses goto()
            try:
                page.goto(URL, wait_until="domcontentloaded", timeout=20000)
            except Exception:
                pass # Ignore first load error

            # --- OPTIMIZATION 2: Reuse the page object by calling reload() ---
            # Subsequent visits are faster because they don't create new pages.
            for visit_num in range(2, num_visits + 1):
                try:
                    page.reload(wait_until="domcontentloaded", timeout=20000)
                except Exception:
                    # In a high-frequency script, we can ignore individual errors
                    pass
            
            browser.close()
            print(f"--- Thread for {platform_name} finished successfully. ---")

    except Exception as e:
        print(f"--- FATAL ERROR in thread for {platform_name}: {e} ---")


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Max-Performance PARALLEL Visitor (v3 - Optimized) ---")
    
    total_visits_to_perform = len(PLATFORM_PROFILES) * TOTAL_VISITS_PER_PLATFORM
    print(f"Attempting {total_visits_to_perform} total visits across {len(PLATFORM_PROFILES)} threads.\n")

    threads = []
    # Create and start all the threads
    for platform, profile in PLATFORM_PROFILES.items():
        thread = threading.Thread(
            target=run_platform_session,
            args=(platform, profile, TOTAL_VISITS_PER_PLATFORM)
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("\n--- All parallel visits complete. ---")