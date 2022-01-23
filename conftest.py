import allure
import pytest
import requests
import json

from selenium import webdriver


def pytest_addoption(parser):
    parser.addoption("--api_url", default="https://jsonplaceholder.typicode.com")
    parser.addoption("--opencart_url", default="https://demo.opencart.com")
    parser.addoption("--browser", default="chrome")
    parser.addoption("--browser_version", action="store", default="93.0")
    parser.addoption("--executor",
                     # имя контейнера в сети selenoid
                     default="selenoid",
                     )
    parser.addoption("--vnc", action="store_true", default=False)
    parser.addoption("--video", action="store_true", default=False)


@pytest.fixture(scope="session")
def api_client(request):
    base_url = request.config.getoption("--api_url")

    class APIClient:
        def __init__(self, base_address):
            self.base_address = base_address

        def post(self, path="/", params=None, data=None, headers=None):
            url = self.base_address + path
            return requests.post(url=url, params=params, data=data, headers=headers, verify=False)

        def get(self, path="/", params=None):
            url = self.base_address + path
            return requests.get(url=url, params=params, verify=False)

    return APIClient(base_address=base_url)


@pytest.fixture
def browser(request):
    browser = request.config.getoption("--browser")
    browser_version = request.config.getoption("--browser_version")
    executor = request.config.getoption("--executor")
    vnc = request.config.getoption("--vnc")
    video = request.config.getoption("--video")
    base_url = request.config.getoption("--opencart_url")

    driver = webdriver.Remote(
        command_executor=f"http://{executor}:4444/wd/hub",
        desired_capabilities={
            "browserName": browser,
            "browserVersion": browser_version,
            "selenoid:options": {
                "enableVNC": vnc,
                "enableVideo": video
            }
        }
    )

    @allure.step("Открываю {url}")
    def open_page(url):
        driver.get(url)

    @allure.step("Проверяю вхождение {target} значения в тайтл страницы")
    def check_in_title(target):
        assert target in driver.title

    driver.base_url = base_url
    driver.open_page = open_page
    driver.check_in_title = check_in_title

    def fin():
        driver.quit()
        requests.delete(f"http://{executor}:4444/wd/hub/session/{driver.session_id}", verify=False)

    allure.attach(body=json.dumps(driver.capabilities), attachment_type=allure.attachment_type.JSON)
    request.addfinalizer(fin)
    return driver
