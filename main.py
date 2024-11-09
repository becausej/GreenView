from rebrowser_playwright.sync_api import sync_playwright, Browser, BrowserContext
import random
import numpy as np
import json

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
        self.page.wait_for_timeout(1500)
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

class AreaScraper(USGSMapScraper):
    def __init__(self, min_lat, min_long, max_lat, max_long):
        super().__init__()
        self.min_lat = min_lat
        self.min_long = min_long
        self.max_lat = max_lat
        self.max_long = max_long

    def scrape_steps(self, lat_step_size, long_step_size, callback):
        lats = np.arange(self.min_lat, self.max_lat, lat_step_size)
        longs = np.arange(self.min_long, self.max_long, long_step_size)

        for lat_index in range(len(lats)):
            for long_index in range(len(longs)):
                lat = str(lats[lat_index])
                long = str(longs[long_index])
                path = f"output/screenshot_{lat_index}_{long_index}.png"
                self.capture(lat, long, path)
                callback(lat, long, path)

def main():
    # with USGSMapScraper() as scraper:
    #     for i, (lat, long) in enumerate([
    #         ('42.3498476225924', '-71.06367409229279'),
    #         ('42.355367352364375', '-71.0640549659729'),
    #         ('42.35453486490882', '-71.0676920413971'),
    #         ('42.3617203219366', '-71.06894731521606'),
    #         ('42.364225392938955', '-71.06598615646362'),
    #     ]):
    #         print(f"Capturing screenshot {i}")
    #         scraper.capture(lat, long, f"output/screenshot_{i}.png")

    features = []

    def callback(lat, long, path):
        feature = {
            "type": "Feature",
            "properties": {
                "green": 1
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(long), float(lat)]
            }
        }
        features.append(feature)

    with AreaScraper(42.3491, -71.0725, 42.3678, -71.0486) as scraper:
        scraper.scrape_steps(0.0025, 0.004, callback)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open("output/geojson.json", "w") as f:
        json.dump(geojson, f)

if __name__ == "__main__":
    main()
