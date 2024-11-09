from playwright.sync_api import sync_playwright, Browser, BrowserContext

class USGSMapScraper:
    URL = "https://earthexplorer.usgs.gov/"
    RADIUS = "100"

    def __init__(self, headless: bool = False):
        self.playwright = sync_playwright().start()
        self.browser: Browser = self.playwright.chromium.launch(headless=headless)
        self.context: BrowserContext = self.browser.new_context()

    def capture(self, latitude: str, longitude: str, output_path: str = "screenshot.png"):
        """
        Capture a screenshot of the USGS Earth Explorer map for given coordinates

        Args:
            latitude (str): The latitude coordinate
            longitude (str): The longitude coordinate
            output_path (str): Path where the screenshot will be saved
        """
        page = self.context.new_page()
        page.goto(self.URL)
        page.wait_for_selector("#tabCircle")
        page.click("#tabCircle")
        page.wait_for_selector("#centerLat")
        page.locator("#centerLat").press_sequentially(latitude)
        page.locator("#centerLng").press_sequentially(longitude)
        page.fill("#circleRadius", self.RADIUS)
        page.click("#circleEntryApply")

        # hover over #map and scroll up to zoom in
        page.hover("#map")
        page.mouse.wheel(0, -1000)
        page.click("#circleEntryClear")
        page.wait_for_timeout(500)
        page.locator("#map").screenshot(path=output_path)
        page.close()

    def close(self):
        """
        Close the browser and playwright instance
        """
        self.browser.close()
        self.playwright.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    with USGSMapScraper(headless=False) as scraper:
        for i, (lat, long) in enumerate([
            ('42.3498476225924', '-71.06367409229279'),
            ('42.355367352364375', '-71.0640549659729'),
            ('42.35453486490882', '-71.0676920413971'),
            ('42.3617203219366', '-71.06894731521606'),
            ('42.364225392938955', '-71.06598615646362'),
        ]):
            scraper.capture(lat, long, f"screenshot_{i}.png")


if __name__ == "__main__":
    main()
