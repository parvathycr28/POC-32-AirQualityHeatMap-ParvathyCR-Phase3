import os
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


TARGETS = {
    "preview": "https://poc32-phase3-frontend-preview.onrender.com/data-intelligence",
    "production": "https://poc32-phase3-frontend.onrender.com/data-intelligence",
}

ARTIFACT_DIR = Path("selenium-test/selenium_artifacts/data_intelligence")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_POLLUTANTS = {"NO₂", "O₃", "PM10", "PM2.5"}
EXPECTED_CITIES = 8


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1100")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)


def run_test(name, url):
    print(f"\n{'=' * 60}")
    print(f"DATA INTELLIGENCE — {name.upper()}")
    print(f"{'=' * 60}")

    driver = create_driver()
    wait = WebDriverWait(driver, 60)
    passed = 0
    failed = 0

    def check(description, condition):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"[PASS] {description}")
        else:
            failed += 1
            print(f"[FAIL] {description}")

    try:
        driver.get(url)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h1[normalize-space()='Data Intelligence']")
        ))
        check("Public Data Intelligence page opens", True)

        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, "//*[@role='status']")
        ))

        alerts = driver.find_elements(By.XPATH, "//*[@role='alert']")
        check("Approved results load without an API error", not alerts)

        if alerts:
            print("       API message:", alerts[0].text[:300])
            return passed, failed

        page_text = driver.find_element(By.TAG_NAME, "body").text
        check("32 approved results are displayed",
              "Published results" in page_text and
              "32" in page_text)
        check("Expected data version is displayed",
              "phase3-v1.1" in page_text)
        check("Expected method version is displayed",
              "track-a-comparative-v1.0.0" in page_text)

        comparison = driver.find_element(
            By.XPATH,
            "//h2[normalize-space()='City Comparison']/ancestor::section[1]"
        )
        chart_articles = comparison.find_elements(By.XPATH, "./article")

        chart_names = {
            article.find_element(By.TAG_NAME, "h3").text.strip()
            for article in chart_articles
        }
        check("All four pollutant comparison charts are present",
              EXPECTED_POLLUTANTS.issubset(chart_names))

        eight_city_labels = 0
        for article in chart_articles:
            labels = article.find_elements(
                By.XPATH, ".//span[normalize-space()='8 cities']"
            )
            if labels:
                eight_city_labels += 1

        check("Each pollutant chart reports eight cities",
              len(chart_articles) == 4 and eight_city_labels == 4)

        selects = driver.find_elements(By.TAG_NAME, "select")
        check("Pollutant and city filters are present", len(selects) >= 2)

        if len(selects) >= 2:
            pollutant_select = Select(selects[0])
            pollutant_options = [
                option.get_attribute("value")
                for option in pollutant_select.options
            ]
            chosen_pollutant = next(
                (value for value in pollutant_options
                 if value not in ("", "all")),
                None
            )

            if chosen_pollutant:
                pollutant_select.select_by_value(chosen_pollutant)
                time.sleep(1)
                filtered_charts = comparison.find_elements(
                    By.XPATH, "./article"
                )
                check("Pollutant filter changes comparison charts",
                      len(filtered_charts) == 1)
                pollutant_select.select_by_value("all")

            city_select = Select(selects[1])
            city_options = [
                option.get_attribute("value")
                for option in city_select.options
            ]
            chosen_city = next(
                (value for value in city_options
                 if value not in ("", "all")),
                None
            )

            if chosen_city:
                city_select.select_by_value(chosen_city)
                time.sleep(1)
                shown_text = driver.find_element(
                    By.XPATH, "//p[contains(., 'Showing')]"
                ).text
                check("City filter updates the displayed result count",
                      "Showing" in shown_text and "of 32 results" in shown_text)
                city_select.select_by_value("all")

        assistant_links = driver.find_elements(
            By.XPATH,
            "//a[contains(normalize-space(.), 'Ask Assistant about this finding')]"
        )
        check("Result-specific Assistant handoff link is available",
              len(assistant_links) > 0)

        if assistant_links:
            first_link = assistant_links[0]
            href = first_link.get_attribute("href")
            parsed = urlparse(href)
            query = parse_qs(parsed.query)
            result_id = query.get("resultId", [""])[0]

            check("Assistant handoff includes a result ID",
                  parsed.path.endswith("/assistant") and bool(result_id))

            driver.save_screenshot(
                str(ARTIFACT_DIR / f"{name}_data_intelligence.png")
            )

            driver.get(href)
            wait.until(lambda d: "/assistant" in d.current_url)
            current_query = parse_qs(urlparse(driver.current_url).query)
            check("Assistant handoff opens with the selected result ID",
                  current_query.get("resultId", [""])[0] == result_id)

        else:
            driver.save_screenshot(
                str(ARTIFACT_DIR / f"{name}_data_intelligence.png")
            )

    except Exception as exc:
        failed += 1
        print(f"[FAIL] Test execution error: {type(exc).__name__}: {exc}")
        try:
            driver.save_screenshot(
                str(ARTIFACT_DIR / f"{name}_failure.png")
            )
        except Exception:
            pass
    finally:
        driver.quit()

    print(f"\n{name.upper()} RESULT: {passed} passed, {failed} failed")
    return passed, failed


if __name__ == "__main__":
    total_passed = 0
    total_failed = 0

    for name, url in TARGETS.items():
        passed, failed = run_test(name, url)
        total_passed += passed
        total_failed += failed

    print("\n" + "=" * 60)
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    print(f"SCREENSHOTS: {ARTIFACT_DIR.resolve()}")
    print("=" * 60)

    raise SystemExit(1 if total_failed else 0)
