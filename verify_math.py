import time
from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        time.sleep(5)

        page.locator("label").filter(has_text="Brain Training").click(force=True)
        time.sleep(3)

        page.locator("label").filter(has_text="Leicht").click(force=True)
        time.sleep(1)

        page.locator("label").filter(has_text="Multiplikation").click(force=True)
        time.sleep(1)

        page.locator("text=SPRINT 1 STARTEN").click(force=True)
        time.sleep(3)

        # Focus first result input via DOM manipulation instead of tab if tab is flaky
        # Let's fill ONLY the result inputs to visually verify the smaller Merkzahlen.
        # But wait, let's type into the rightmost main field to test the focus jump!

        # Focus on the rightmost step field (step_0_last)
        step_inputs = page.locator('input[aria-label^="step_0_"]').all()
        if step_inputs:
            # Type '3' in the last input
            step_inputs[-1].focus()
            step_inputs[-1].type('3', delay=100)
            time.sleep(1)

            # The focus should now be on the merk_0_(last-1) field.
            # We can take a screenshot to verify where the focus ring is!
            page.screenshot(path="math_expert_wrong.png")

        print("Test finished.")

        print("Test finished.")
        browser.close()

if __name__ == "__main__":
    verify()
