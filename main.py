from re import sub
from rebrowser_playwright.sync_api import sync_playwright, Browser, BrowserContext
import numpy as np
import json
from detection import one_img
import os
from tqdm import tqdm

testing_mode = False

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

        progress = tqdm(total=len(lats) * len(longs))

        for lat_index in range(len(lats)):
            for long_index in range(len(longs)):
                lat = str(lats[lat_index])
                long = str(longs[long_index])
                path = f"output/screenshot_{lat_index}_{long_index}.png"
                if not os.path.exists(path):
                    self.capture(lat, long, path)
                callback(lat, long, path)
                progress.update(1)

def main():
    lat_step_size = 0.0025
    long_step_size = 0.004

    if testing_mode:
        lat_step_size *= 5
        long_step_size *= 5

    features = []

    def callback(lat, long, path):
        num_row = 3
        num_col = 3

        green = one_img(path, num_row=num_row, num_col=num_col) ** 1
        lat_float = float(lat)
        long_float = float(long)

        left = long_float - long_step_size / 2
        bottom = lat_float - lat_step_size / 2

        for row in range(num_row):
            for col in range(num_col):
                g = green[-1-row, col]

                r_amount = 1 * g
                g_amount = 2 * g
                b_amount = 1 * g
                def num_to_hex_digits(num):
                    if num > 1:
                        num = 1
                    hex_str = hex(int(num * 255))[2:]
                    if len(hex_str) == 1:
                        hex_str = "0" + hex_str
                    return hex_str

                color = f"#{num_to_hex_digits(r_amount)}{num_to_hex_digits(g_amount)}{num_to_hex_digits(b_amount)}"

                sub_bottom = bottom + row / num_row * lat_step_size
                sub_top = bottom + (row + 1) / num_row * lat_step_size
                sub_left = left + col / num_col * long_step_size
                sub_right = left + (col + 1) / num_col * long_step_size

                feature = {
                    "type": "Feature",
                    "properties": {
                        "green": float(g),
                        "fill": color,
                        "fill-opacity": 0.6,
                        "stroke": "#000000",
                        "stroke-width": 1,
                        "stroke-opacity": 1,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [
                                sub_left, sub_top,
                            ],
                            [
                                sub_right, sub_top,
                            ],
                            [
                                sub_right, sub_bottom,
                            ],
                            [
                                sub_left, sub_bottom,
                            ],
                            [
                                sub_left, sub_top,
                            ],
                        ]],
                    },
                }

                features.append(feature)

    with AreaScraper(42.3241, -71.1025, 42.3928, -71.0186) as scraper:
        scraper.scrape_steps(lat_step_size, long_step_size, callback)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open("output/geojson.json", "w") as f:
        json.dump(geojson, f)

if __name__ == "__main__":
    main()
