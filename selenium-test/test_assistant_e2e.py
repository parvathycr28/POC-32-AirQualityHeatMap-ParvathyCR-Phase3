import os
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.getenv("ASSISTANT_URL", "http://localhost:3002/assistant")

ARTIFACT_DIR = Path(__file__).resolve().parent / "selenium_artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

SCREENSHOT_PATH = ARTIFACT_DIR / "assistant_e2e.png"
REPORT_PATH = ARTIFACT_DIR / "Assistant_Test_Report.txt"
RESPONSIVE_WIDTHS = (1440, 768, 390, 320)


class AssistantE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = Options()

        if os.getenv("HEADLESS", "1") == "1":
            options.add_argument("--headless=new")

        options.add_argument("--window-size=1440,1000")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        cls.driver = webdriver.Chrome(options=options)
        cls.wait = WebDriverWait(cls.driver, 30)
        cls.results = []

    @classmethod
    def tearDownClass(cls):
        try:
            if getattr(cls, "driver", None):
                cls.driver.quit()
        finally:
            lines = [
                "INFOCREON POC-32 - GROUNDED DATA ASSISTANT E2E REPORT",
                "=" * 60,
                f"Assistant URL: {BASE_URL}",
                f"Executed: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
            ]

            lines.extend(cls.results)

            passed = sum("[PASS]" in line for line in cls.results)
            failed = sum("[FAIL]" in line for line in cls.results)

            lines.extend([
                "",
                f"Passed: {passed}",
                f"Failed: {failed}",
                f"Result: {'PASS' if failed == 0 else 'FAIL'}",
                f"Screenshot: {SCREENSHOT_PATH}",
            ])

            REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
            print("\n".join(lines))

    def record(self, name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        self.results.append(
            f"[{status}] {name}" + (f" — {details}" if details else "")
        )

    def ask(self, question):
        field = self.wait.until(
            EC.visibility_of_element_located((By.ID, "assistant-question"))
        )
        field.clear()
        field.send_keys(question)

        button = self.driver.find_element(
            By.XPATH,
            "//button[@type='submit' and contains(., 'Ask assistant')]"
        )
        button.click()

        self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h2[normalize-space()='Assistant response']")
            )
        )

        self.wait.until(
            lambda d: "Checking evidence..." not in d.find_element(
                By.XPATH, "//form//button[@type='submit']"
            ).text
        )

        return self.driver.find_element(
            By.XPATH,
            "//h2[normalize-space()='Assistant response']/ancestor::section"
        )

    def test_01_page_loads(self):
        self.driver.get(BASE_URL)

        heading = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//h1[normalize-space()='Grounded Data Assistant']")
            )
        )

        self.assertTrue(heading.is_displayed())
        self.assertTrue(
            self.driver.find_element(By.ID, "assistant-question").is_displayed()
        )

        self.record("Assistant page loads", True)

    def test_02_supported_comparison_returns_evidence(self):
        response = self.ask("Compare Delhi and Mumbai for no2")
        text = response.text
        evidence_heading = response.find_element(
            By.XPATH, ".//*[contains(., 'Supporting evidence (')]"
        )

        self.assertIn("Assistant response", text)
        self.assertIn("Supporting evidence", evidence_heading.text)
        self.assertRegex(
            evidence_heading.text, r"Supporting evidence \([1-9]\d*\)"
        )

        self.record(
            "Supported comparison displays evidence",
            True,
            evidence_heading.text
        )
        self.driver.save_screenshot(str(SCREENSHOT_PATH))

    def test_03_unsupported_prediction_is_rejected(self):
        response = self.ask("Predict tomorrow's NO2 level in Delhi")
        text = response.text.lower()

        status = response.find_element(By.XPATH, ".//span").text.strip().lower()

        self.assertIn(status, ("unsupported", "refused", "rejected"))
        self.assertIn("supporting evidence (0)", text)

        self.record(
            "Unsupported prediction rejected without evidence",
            True,
            f"status={status}; evidence=0"
        )

    def test_04_responsive_layout_at_required_widths(self):
        self.driver.get(BASE_URL)
        self.wait.until(
            EC.visibility_of_element_located((By.ID, "assistant-question"))
        )

        width_results = []

        try:
            for width in RESPONSIVE_WIDTHS:
                # Set the webpage's CSS viewport directly, not the outer
                # Chrome window dimensions.
                self.driver.execute_cdp_cmd(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": width,
                        "height": 900,
                        "deviceScaleFactor": 1,
                        "mobile": False,
                    },
                )

                self.driver.refresh()
                self.wait.until(
                    EC.visibility_of_element_located(
                        (By.ID, "assistant-question")
                    )
                )

                dimensions = self.driver.execute_script("""
                    return {
                        viewport: window.innerWidth,
                        documentClient: document.documentElement.clientWidth,
                        documentScroll: document.documentElement.scrollWidth,
                        bodyScroll: document.body.scrollWidth
                    };
                """)

                actual_viewport = dimensions["viewport"]
                document_width = dimensions["documentScroll"]
                body_width = dimensions["bodyScroll"]

                no_overflow = (
                    actual_viewport == width
                    and document_width <= actual_viewport + 1
                    and body_width <= actual_viewport + 1
                )

                result = (
                    f"{width}px requested: viewport={actual_viewport}, "
                    f"document={document_width}, body={body_width}, "
                    f"overflow={'NO' if no_overflow else 'YES'}"
                )
                width_results.append(result)

                self.assertTrue(
                    no_overflow,
                    f"Responsive check failed at {width}px: "
                    f"{dimensions}; expected viewport={width}"
                )

            self.record(
                "Responsive layout at 1440, 768, 390, and 320 px",
                True,
                " | ".join(width_results)
            )
        finally:
            self.driver.execute_cdp_cmd(
                "Emulation.clearDeviceMetricsOverride", {}
            )

        self.driver.save_screenshot(str(SCREENSHOT_PATH))


if __name__ == "__main__":
    unittest.main(verbosity=2)
