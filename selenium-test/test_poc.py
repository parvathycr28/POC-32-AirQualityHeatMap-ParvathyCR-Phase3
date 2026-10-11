
import json
import os
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


# ============================================================
# CONFIGURATION
# ============================================================

# Deployed operational dashboard
BASE_URL = "https://poc-32-airqualityheatmap-frontend.onrender.com"

# Local Data Intelligence frontend.
# Change port 3000 to 5173 if that is the port shown by your frontend.
LOCAL_DATA_INTELLIGENCE_URL = os.getenv(
    "LOCAL_DATA_INTELLIGENCE_URL",
    "http://localhost:3000/data-intelligence",
)

# Local Data Intelligence backend
LOCAL_INTELLIGENCE_API_URL = os.getenv(
    "LOCAL_INTELLIGENCE_API_URL",
    "http://127.0.0.1:8000/api/intelligence/results",
)

WAIT_SECONDS = 45

ARTIFACT_DIR = Path(__file__).resolve().parent / "selenium_artifacts"
SCREENSHOT_PATH = ARTIFACT_DIR / "aether_pulse_e2e.png"
REPORT_PATH = ARTIFACT_DIR / "Test_Report.txt"


# ============================================================
# DRIVER
# ============================================================

def build_driver() -> webdriver.Chrome:
    options = Options()

    if os.getenv("HEADLESS", "0") == "1":
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.set_capability(
        "goog:loggingPrefs",
        {"performance": "ALL"},
    )

    return webdriver.Chrome(options=options)


# ============================================================
# HELPERS
# ============================================================

def wait_for_data(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
) -> None:
    wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                'button[aria-label^="View air quality details for "]',
            )
        )
    )


def get_air_quality_responses(
    driver: webdriver.Chrome,
) -> list[dict]:
    responses = []

    for entry in driver.get_log("performance"):
        try:
            message = json.loads(entry["message"])["message"]
        except (KeyError, TypeError, json.JSONDecodeError):
            continue

        if message.get("method") != "Network.responseReceived":
            continue

        response = message.get("params", {}).get("response", {})
        url = response.get("url", "")

        if "/api/air-quality" in url:
            responses.append(
                {
                    "url": url,
                    "status": int(response.get("status", 0)),
                }
            )

    return responses


def write_report(
    results: list[tuple[str, str, str]],
) -> None:
    passed = sum(status == "PASS" for _, status, _ in results)
    total = len(results)
    overall = "PASS" if passed == total else "FAIL"

    lines = [
        "INFOCREON POC-32 - SELENIUM E2E TEST REPORT",
        "=" * 52,
        f"Operational dashboard: {BASE_URL}",
        f"Local Data Intelligence page: {LOCAL_DATA_INTELLIGENCE_URL}",
        f"Executed: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]

    for name, status, detail in results:
        lines.append(f"[{status}] {name}")
        lines.append(f"       {detail}")

    lines.extend(
        [
            "",
            f"Result: {overall}",
            f"Passed: {passed}/{total}",
            f"Screenshot: {SCREENSHOT_PATH}",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def add_result(
    results: list[tuple[str, str, str]],
    name: str,
    status: str,
    detail: str,
) -> None:
    results.append((name, status, detail))


# ============================================================
# MAIN TEST
# ============================================================

def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    driver = None
    results: list[tuple[str, str, str]] = []

    try:
        driver = build_driver()
        wait = WebDriverWait(driver, WAIT_SECONDS)

        # --------------------------------------------------------
        # 1. DEPLOYED OPERATIONAL URL OPENS
        # --------------------------------------------------------

        try:
            driver.get(BASE_URL)

            wait.until(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete"
            )

            add_result(
                results,
                "Operational URL opens",
                "PASS",
                f"Opened {driver.current_url}",
            )

        except Exception as exc:
            add_result(
                results,
                "Operational URL opens",
                "FAIL",
                str(exc),
            )
            raise

        # --------------------------------------------------------
        # 2. MAIN DASHBOARD LOADS
        # --------------------------------------------------------

        try:
            wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//h2[normalize-space()='Air Quality Heatmap']",
                    )
                )
            )

            wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//*[normalize-space()='REAL RAILS']",
                    )
                )
            )

            add_result(
                results,
                "Main dashboard loads",
                "PASS",
                "REAL RAILS and Air Quality Heatmap are visible.",
            )

        except Exception as exc:
            add_result(
                results,
                "Main dashboard loads",
                "FAIL",
                str(exc),
            )

        # --------------------------------------------------------
        # 3. LEAFLET VISUALIZATION
        # --------------------------------------------------------

        try:
            wait.until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "div.leaflet-container",
                    )
                )
            )

            add_result(
                results,
                "Core visualization appears",
                "PASS",
                "Leaflet map container is visible.",
            )

        except TimeoutException:
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".leaflet-tile-pane, "
                            ".leaflet-marker-icon, "
                            ".leaflet-overlay-pane",
                        )
                    )
                )

                add_result(
                    results,
                    "Core visualization appears",
                    "PASS",
                    "Leaflet map content is rendered.",
                )

            except Exception as exc:
                add_result(
                    results,
                    "Core visualization appears",
                    "FAIL",
                    f"Leaflet content was not detected: {exc}",
                )

        except Exception as exc:
            add_result(
                results,
                "Core visualization appears",
                "FAIL",
                str(exc),
            )

        # --------------------------------------------------------
        # 4. OPERATIONAL API AND CITY DATA
        # --------------------------------------------------------

        try:
            wait_for_data(driver, wait)

            backend_responses = get_air_quality_responses(driver)

            successful = [
                item
                for item in backend_responses
                if item["status"] == 200
            ]

            if not successful:
                raise AssertionError(
                    "No successful /api/air-quality response found. "
                    f"Observed: {backend_responses}"
                )

            add_result(
                results,
                "Operational API communication",
                "PASS",
                f"Successful API response: {successful[-1]['url']}",
            )

            add_result(
                results,
                "Operational data is loaded",
                "PASS",
                "At least one city data card is rendered.",
            )

        except Exception as exc:
            add_result(
                results,
                "Operational API communication",
                "FAIL",
                str(exc),
            )

            add_result(
                results,
                "Operational data is loaded",
                "FAIL",
                str(exc),
            )

        # --------------------------------------------------------
        # 5. POLLUTANT FILTER
        # --------------------------------------------------------

        try:
            pollutant = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'select[aria-label="Select pollutant"]',
                    )
                )
            )

            select = Select(pollutant)
            original_value = select.first_selected_option.get_attribute(
                "value"
            )

            target_value = (
                "PM10" if original_value != "PM10" else "PM2.5"
            )

            select.select_by_value(target_value)

            wait.until(
                lambda d: d.find_element(
                    By.CSS_SELECTOR,
                    'select[aria-label="Select pollutant"]',
                ).get_attribute("value") == target_value
            )

            add_result(
                results,
                "Pollutant filter interaction",
                "PASS",
                f"Changed pollutant from {original_value} "
                f"to {target_value}.",
            )

            Select(
                driver.find_element(
                    By.CSS_SELECTOR,
                    'select[aria-label="Select pollutant"]',
                )
            ).select_by_value("PM2.5")

        except Exception as exc:
            add_result(
                results,
                "Pollutant filter interaction",
                "FAIL",
                str(exc),
            )

        # --------------------------------------------------------
        # 6. OPERATIONAL INTELLIGENCE PANEL
        # --------------------------------------------------------

        try:
            open_panel = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[normalize-space()='Intelligence Panel']",
                    )
                )
            )

            open_panel.click()

            wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//h2[normalize-space()='Intelligence panel']",
                    )
                )
            )

            close_panel = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'button[aria-label="Close intelligence panel"]',
                    )
                )
            )

            close_panel.click()

            wait.until(
                EC.invisibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'button[aria-label="Close intelligence panel"]',
                    )
                )
            )

            add_result(
                results,
                "Operational intelligence panel",
                "PASS",
                "Panel opened and closed successfully.",
            )

        except Exception as exc:
            add_result(
                results,
                "Operational intelligence panel",
                "FAIL",
                str(exc),
            )

        # --------------------------------------------------------
        # 7. LOCAL DATA INTELLIGENCE PAGE
        # --------------------------------------------------------

        try:
            driver.get(LOCAL_DATA_INTELLIGENCE_URL)

            intelligence_wait = WebDriverWait(driver, 60)

            intelligence_wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//h1[normalize-space()='Data Intelligence']",
                    )
                )
            )

            page_text = driver.find_element(
                By.TAG_NAME,
                "body",
            ).text

            if "Results could not be loaded" in page_text:
                raise AssertionError(
                    "Data Intelligence results failed to load."
                )

            add_result(
                results,
                "Local Data Intelligence page",
                "PASS",
                f"Page loaded: {driver.current_url}",
            )

        except Exception as exc:
            add_result(
                results,
                "Local Data Intelligence page",
                "FAIL",
                f"{LOCAL_DATA_INTELLIGENCE_URL}: {exc}",
            )

        # --------------------------------------------------------
        # 8. LOCAL DATA INTELLIGENCE API CHECK
        # --------------------------------------------------------
        # Open the API URL directly in the browser and verify that
        # the endpoint responds with HTTP 200.
        # This check does not depend on the page's frontend fetch.

        try:
            driver.get(LOCAL_INTELLIGENCE_API_URL)

            api_wait = WebDriverWait(driver, 15)

            api_wait.until(
                lambda d: d.execute_script(
                    "return document.readyState"
                ) == "complete"
            )

            api_status = driver.execute_script(
                """
                return fetch(arguments[0], {method: 'GET'})
                    .then(response => response.status)
                    .catch(() => 0);
                """,
                LOCAL_INTELLIGENCE_API_URL,
            )

            if api_status != 200:
                raise AssertionError(
                    f"Intelligence API returned status {api_status}."
                )

            add_result(
                results,
                "Local Data Intelligence API",
                "PASS",
                f"API returned HTTP {api_status}.",
            )

        except Exception as exc:
            add_result(
                results,
                "Local Data Intelligence API",
                "FAIL",
                str(exc),
            )

        # --------------------------------------------------------
        # 9. RESPONSIVE OPERATIONAL DASHBOARD CHECK
        # --------------------------------------------------------

        try:
            # Return to the deployed operational dashboard for
            # the original responsive regression test.
            driver.set_window_size(390, 844)
            driver.get(BASE_URL)

            mobile_wait = WebDriverWait(driver, WAIT_SECONDS)

            mobile_wait.until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//h2[normalize-space()='Air Quality Heatmap']",
                    )
                )
            )

            no_horizontal_overflow = driver.execute_script(
                """
                return document.documentElement.scrollWidth
                    <= window.innerWidth + 2;
                """
            )

            if not no_horizontal_overflow:
                raise AssertionError(
                    "Horizontal overflow detected at 390px width."
                )

            add_result(
                results,
                "Operational responsive check",
                "PASS",
                "Dashboard rendered at 390x844 without "
                "horizontal overflow.",
            )

        except Exception as exc:
            add_result(
                results,
                "Operational responsive check",
                "FAIL",
                str(exc),
            )

        # --------------------------------------------------------
        # 10. SCREENSHOT
        # --------------------------------------------------------

        try:
            screenshot_saved = driver.save_screenshot(
                str(SCREENSHOT_PATH)
            )

            if not screenshot_saved or not SCREENSHOT_PATH.exists():
                raise AssertionError("Screenshot was not created.")

            add_result(
                results,
                "Screenshot captured",
                "PASS",
                f"Saved to {SCREENSHOT_PATH}",
            )

        except Exception as exc:
            add_result(
                results,
                "Screenshot captured",
                "FAIL",
                str(exc),
            )

    except WebDriverException as exc:
        if not any(
            name == "Operational URL opens"
            for name, _, _ in results
        ):
            add_result(
                results,
                "Operational URL opens",
                "FAIL",
                f"WebDriver error: {exc}",
            )

    finally:
        if driver is not None:
            driver.quit()

        write_report(results)

    # ------------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------------

    overall_pass = all(
        status == "PASS"
        for _, status, _ in results
    )

    print("\n" + "\n".join(
        f"[{status}] {name} — {detail}"
        for name, status, detail in results
    ))

    print(
        f"\nOVERALL RESULT: {'PASS' if overall_pass else 'FAIL'}"
    )
    print(f"REPORT: {REPORT_PATH}")
    print(f"SCREENSHOT: {SCREENSHOT_PATH}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
