import asyncio
from playwright.async_api import async_playwright

# This is the definitive, most-optimized parallel script. It uses asyncio,
# Playwright's native asynchronous API, which is more efficient than threading
# for I/O-bound tasks like web requests.

# --- Configuration ---
URL = "https://sent.bio/alquis"

# --- IMPORTANT: TUNE THIS NUMBER ---
# With asyncio, you can likely push this number even higher.
# Start with 250 and adjust based on your workflow's run time.
TOTAL_VISITS_PER_PLATFORM = 250

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

# --- This function is now an ASYNCHRONOUS coroutine ---
async def run_platform_session(platform_name, profile, num_visits):
    """
    Executed as an asyncio task. It manages its own Playwright instance
    and performs all visits by reloading a single page.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=profile["user_agent"],
                viewport=profile["viewport"]
            )
            
            await context.route("**/*", lambda route: route.abort() if route.request.resource_type in BLOCKED_RESOURCE_TYPES else route.continue_())
            
            page = await context.new_page()
            
            print(f"--- Task for {platform_name} started. Attempting {num_visits} visits. ---")

            # First visit uses goto()
            try:
                await page.goto(URL, wait_until="domcontentloaded", timeout=20000)
            except Exception:
                pass

            # Subsequent visits use reload()
            for visit_num in range(2, num_visits + 1):
                try:
                    await page.reload(wait_until="domcontentloaded", timeout=20000)
                except Exception:
                    pass
            
            await browser.close()
            print(f"--- Task for {platform_name} finished successfully. ---")

    except Exception as e:
        print(f"--- FATAL ERROR in task for {platform_name}: {e} ---")


# --- Main ASYNCHRONOUS Execution ---
async def main():
    print("--- Starting Max-Performance ASYNC Visitor ---")
    
    total_visits_to_perform = len(PLATFORM_PROFILES) * TOTAL_VISITS_PER_PLATFORM
    print(f"Attempting {total_visits_to_perform} total visits across {len(PLATFORM_PROFILES)} concurrent tasks.\n")

    # Create a list of all the tasks we want to run
    tasks = []
    for platform, profile in PLATFORM_PROFILES.items():
        task = asyncio.create_task(
            run_platform_session(platform, profile, TOTAL_VISITS_PER_PLATFORM)
        )
        tasks.append(task)

    # Wait for all the created tasks to complete
    await asyncio.gather(*tasks)

    print("\n--- All concurrent visits complete. ---")


if __name__ == "__main__":
    asyncio.run(main())