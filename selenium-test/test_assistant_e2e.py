
import os
import time
import unittest
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = os.getenv(
    "ASSISTANT_URL",
    "http://localhost:3002/assistant"
)

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
        if getattr(cls, "driver", None):
            cls.driver.quit()

    def record(self, name, passed, details=""):
        status = "PASS" if passed else "FAIL"

        self.__class__.results.append(
            f"[{status}] {name}"
            + (f" — {details}" if details else "")
        )

    def ask(self, question):
        self.driver.get(BASE_URL)

        field = self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "assistant-question")
            )
        )

        field.clear()
        field.send_keys(question)

        button = self.driver.find_element(
            By.XPATH,
            "//form//button[@type='submit']"
        )

        button.click()

        # Wait until the frontend finishes loading.
        self.wait.until(
            lambda d: d.find_element(
                By.XPATH,
                "//form//button[@type='submit']"
            ).is_enabled()
        )

        # Check whether the request failed.
        errors = self.driver.find_elements(
            By.CSS_SELECTOR,
            "[role='alert']"
        )

        visible_errors = [
            error.text.strip()
            for error in errors
            if error.is_displayed() and error.text.strip()
        ]

        if visible_errors:
            raise AssertionError(
                "Assistant displayed an error: "
                + " | ".join(visible_errors)
            )

        # Wait for the actual response, not just the heading.
        response = self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//h2[normalize-space()='Assistant response']"
                    "/ancestor::section"
                )
            )
        )

        return response

    def test_01_page_loads(self):
        self.driver.get(BASE_URL)

        heading = self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "//h1[normalize-space()='Grounded Data Assistant']"
                )
            )
        )

        self.assertTrue(heading.is_displayed())

        self.assertTrue(
            self.driver.find_element(
                By.ID,
                "assistant-question"
            ).is_displayed()
        )

        self.record("Assistant page loads", True)

    def test_02_supported_comparison_returns_evidence(self):
        response = self.ask(
            "Compare Delhi and Mumbai for no2"
        )

        text = response.text

        self.assertIn(
            "Mode: deterministic_plus_llm_explanation",
            text
        )
        self.assertIn("Gemini attempted:", text)
        self.assertIn("LLM used:", text)
        self.assertIn("Explanation validated:", text)
        self.assertIn("Deterministic fallback used:", text)
        self.assertIn("Generated findings:", text)
        self.assertIn(
            "Source: approved_intelligence_results",
            text
        )

        evidence_heading = response.find_element(
            By.XPATH,
            ".//*[contains(., 'Supporting evidence (')]"
        )

        self.assertRegex(
            evidence_heading.text,
            r"Supporting evidence \([1-9]\d*\)"
        )

        self.driver.save_screenshot(
            str(SCREENSHOT_PATH)
        )

        self.record(
            "Supported comparison displays evidence",
            True,
            evidence_heading.text
        )

    def test_03_unsupported_prediction_is_rejected(self):
        response = self.ask(
            "Predict tomorrow's NO2 level in Delhi"
        )

        text = response.text.lower()

        status = response.find_element(
            By.XPATH,
            ".//span"
        ).text.strip().lower()

        self.assertIn(
            status,
            ("unsupported", "refused", "rejected")
        )

        self.assertIn(
            "supporting evidence (0)",
            text
        )

        self.record(
            "Unsupported prediction rejected without evidence",
            True,
            f"status={status}; evidence=0"
        )

    def test_04_responsive_layout_at_required_widths(self):
        self.driver.get(BASE_URL)

        self.wait.until(
            EC.visibility_of_element_located(
                (By.ID, "assistant-question")
            )
        )

        width_results = []

        try:
            for width in RESPONSIVE_WIDTHS:
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
                        documentScroll:
                            document.documentElement.scrollWidth,
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

                width_results.append(
                    f"{width}px requested: "
                    f"viewport={actual_viewport}, "
                    f"document={document_width}, "
                    f"body={body_width}, "
                    f"overflow={'NO' if no_overflow else 'YES'}"
                )

                self.assertTrue(
                    no_overflow,
                    f"Responsive check failed at {width}px: "
                    f"{dimensions}"
                )

            self.driver.save_screenshot(
                str(SCREENSHOT_PATH)
            )

            self.record(
                "Responsive layout at 1440, 768, 390, and 320 px",
                True,
                " | ".join(width_results)
            )

        finally:
            self.driver.execute_cdp_cmd(
                "Emulation.clearDeviceMetricsOverride",
                {}
            )


def write_report(result):
    test_results = getattr(
        AssistantE2ETest,
        "results",
        []
    )

    recorded_passes = sum(
        "[PASS]" in line for line in test_results
    )

    recorded_failures = sum(
        "[FAIL]" in line for line in test_results
    )

    unittest_failures = len(result.failures)
    unittest_errors = len(result.errors)
    skipped = len(result.skipped)

    failed = max(
        unittest_failures + unittest_errors,
        recorded_failures
    )

    passed = max(
        0,
        result.testsRun - failed - skipped
    )

    report_result = (
        "PASS"
        if result.wasSuccessful() and recorded_failures == 0
        else "FAIL"
    )

    lines = [
        "INFOCREON POC-32 - GROUNDED DATA ASSISTANT E2E REPORT",
        "=" * 60,
        f"Assistant URL: {BASE_URL}",
        f"Executed: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        *test_results,
        "",
        f"Tests executed: {result.testsRun}",
        f"Recorded passes: {recorded_passes}",
        f"Recorded failures: {recorded_failures}",
        f"Unittest failures: {unittest_failures}",
        f"Unittest errors: {unittest_errors}",
        f"Skipped: {skipped}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        f"Result: {report_result}",
        f"Screenshot: {SCREENSHOT_PATH}",
    ]

    REPORT_PATH.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print("\n".join(lines))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        AssistantE2ETest
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    write_report(result)

    if not result.wasSuccessful() or any(
        "[FAIL]" in line
        for line in getattr(AssistantE2ETest, "results", [])
    ):
        raise SystemExit(1)
