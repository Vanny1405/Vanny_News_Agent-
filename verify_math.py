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
        # We fill the bottom result boxes. Wait, the layout changed!
        # Now there are Merkzahlen, intermediate steps, and the result row.
        # Let's fill ONLY the result inputs to check if the empty check works.
        inputs = page.locator('input[aria-label^="res_"]').all()

        for i, inp in enumerate(inputs):
            inp.fill(str(i+1))
            time.sleep(0.2)

        # Submit form with Enter key
        page.keyboard.press("Enter")
        time.sleep(3)

        page.screenshot(path="math_expert_wrong.png")

        print("Test finished.")
        browser.close()

if __name__ == "__main__":
    verify()
