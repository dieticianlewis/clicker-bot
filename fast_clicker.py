import time
import threading
from playwright.sync_api import sync_playwright, TimeoutError

# This script uses parallel processing (multi-threading) for maximum performance.
# It is now thread-safe by creating an isolated BrowserContext for each thread,
# which is the correct way to use Playwright in a parallel environment.

# --- Configuration ---
URL = "https://sent.bio/alquis"

# --- IMPORTANT: TUNE THIS NUMBER ---
# Start with 60. If your workflow finishes in less than 50 seconds, increase it.
# If it takes more than 60 seconds, decrease it.
TOTAL_VISITS_PER_PLATFORM = 60

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

# --- This function contains the work that EACH thread will do ---
def run_platform_session(browser, platform_name, profile, num_visits):
    """
    This function is executed by a single thread. It performs all the visits
    for one specific platform within its own isolated browser context.
    """
    context = None
    try:
        # --- FIX: Create an isolated BrowserContext for this thread ---
        context = browser.new_context(
            user_agent=profile["user_agent"],
            viewport=profile["viewport"]
        )
        print(f"--- Thread for {platform_name} started. Attempting {num_visits} visits. ---")

        for visit_num in range(1, num_visits + 1):
            page = None
            try:
                page = context.new_page()
                
                # Block unnecessary network resources
                page.route("**/*", lambda route: route.abort() if route.request.resource_type in BLOCKED_RESOURCE_TYPES else route.continue_())
                
                page.goto(URL, wait_until="domcontentloaded", timeout=20000)
                
            except Exception:
                # In a high-frequency script, we can ignore individual errors to keep going
                pass
            finally:
                if page:
                    page.close()
        
        print(f"--- Thread for {platform_name} finished successfully. ---")

    except Exception as e:
        print(f"--- FATAL ERROR in thread for {platform_name}: {e} ---")
    finally:
        # --- FIX: Ensure the context is closed to clean up resources ---
        if context:
            context.close()


# --- Main Execution ---
if __name__ == "__main__":
    print("--- Starting Max-Performance PARALLEL Visitor ---")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        total_visits_to_perform = len(PLATFORM_PROFILES) * TOTAL_VISITS_PER_PLATFORM
        print(f"Browser launched. Will attempt {total_visits_to_perform} total visits across {len(PLATFORM_PROFILES)} threads.\n")

        threads = []
        for platform, profile in PLATFORM_PROFILES.items():
            thread = threading.Thread(
                target=run_platform_session,
                args=(browser, platform, profile, TOTAL_VISITS_PER_PLATFORM)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        browser.close()
        print("\n--- All parallel visits complete. ---")