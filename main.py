from rebrowser_playwright.sync_api import sync_playwright, Browser, BrowserContext

class USGSMapScraper:
    URL = "https://earthexplorer.usgs.gov/"
    RADIUS = "100"

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser: Browser = self.playwright.chromium.launch(
            headless=False,
        )
        self.context: BrowserContext = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(self.URL)
        self.page.wait_for_selector("#tabCircle")
        self.page.click("#tabCircle")
        self.page.wait_for_selector("#centerLat")

    def capture(self, latitude: str, longitude: str, output_path: str = "output/screenshot.png"):
        """
        Capture a screenshot of the USGS Earth Explorer map for given coordinates

        Args:
            latitude (str): The latitude coordinate
            longitude (str): The longitude coordinate
            output_path (str): Path where the screenshot will be saved
        """
        self.page.locator("#centerLat").press_sequentially(latitude)
        self.page.locator("#centerLng").press_sequentially(longitude)
        self.page.fill("#circleRadius", self.RADIUS)
        self.page.click("#circleEntryApply")

        # hover over #map and scroll up to zoom in
        self.page.click("#circleEntryClear")
        self.page.wait_for_timeout(1000)
        self.page.locator("#map").screenshot(path=output_path)

    def close(self):
        """
        Close the browser and playwright instance
        """
        self.page.close()
        self.browser.close()
        self.playwright.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    with USGSMapScraper() as scraper:
        for i, (lat, long) in enumerate([
            ('42.3498476225924', '-71.06367409229279'),
            ('42.355367352364375', '-71.0640549659729'),
            ('42.35453486490882', '-71.0676920413971'),
            ('42.3617203219366', '-71.06894731521606'),
            ('42.364225392938955', '-71.06598615646362'),
        ]):
            print(f"Capturing screenshot {i}")
            scraper.capture(lat, long, f"output/screenshot_{i}.png")

    import os
    print(os.listdir("/app/output"))

if __name__ == "__main__":
    main()
