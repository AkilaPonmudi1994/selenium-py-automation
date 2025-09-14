##Selenium Pytest Automation


This project contains automated UI tests written in **Python**, using Selenium and Pytest


## Prerequisites


Before running tests, make sure you have:


* **Python 3.8+** installed
* **Google Chrome** browser installed


## Setup Project


Clone the repository and install dependencies:


```bash
git clone <repo-url>
cd <repo-folder>
pip install -r requirements.txt
```


---


## Verify Pytest Installation


Check pytest version:


```bash
pytest --version
```


## Running Tests


### Run all tests


```bash
pytest -v --alluredir=allure-results tests.py
```
### Run a specific test


```bash
Pytest -v --alluredir=allure-results test.py::TestHealthAI::test_login
```


## Allure Reporting


### Run tests with Allure plugin


```bash
pytest --alluredir=allure-results
```


### Generate & open the report


```bash
allure serve allure-results
```




## Project Structure


```
.
├── conftest.py         # Pytest fixtures (setup/teardown, hooks)
├── test.py             # Test cases
├── requirements.txt    # Python dependencies
└── README.md           # Project setup & usage guide
```


---


## Failure Screenshots


* On test failure, screenshots are **automatically attached to Allure reports**.
* Files are stored in `allure-results/` with unique UUID-based names (by Allure).
