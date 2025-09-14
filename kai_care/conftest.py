import pytest
import allure


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to store test result for screenshot fixture"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        driver = getattr(item.instance, "driver", None)
        if driver:
            allure.attach(
                driver.get_screenshot_as_png(),
                name=f"{item.name}_screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
