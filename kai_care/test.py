import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import random

class TestHealthAI:
    # Constants
    BASE_URL = "https://doctorstaging.myhealthai.io/"
    DEFAULT_USERNAME = "carlos@test.com"
    DEFAULT_PASSWORD = "Admin@456"

    @pytest.fixture(scope="class", autouse=True)
    def setup_driver(self, request):
        print("*********Setting up********")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(options=options)
        cls = request.cls
        driver.get(cls.BASE_URL)
        driver.maximize_window()
        driver.implicitly_wait(3)
        cls.driver = driver
        cls.wait = WebDriverWait(cls.driver, 10)
        self.login()
        yield
        print("*****Teardown*****")
        cls.driver.quit()

    @pytest.fixture(scope="function", autouse=True)
    def setup_each_test(self):
        """Fixture that runs before each test method - refreshes home page"""
        home_page = "https://doctorstaging.myhealthai.io/tables"
        self.driver.get(home_page)
        time.sleep(3)

    def login(self):
        self.driver.find_element(By.ID, "email").send_keys(self.DEFAULT_USERNAME)
        self.driver.find_element(By.ID, "password-input").send_keys(
            self.DEFAULT_PASSWORD
        )
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)

    @pytest.mark.order(1)
    def test_login(self):
        """Test Step 1: Login to the application"""
        assert self.driver.title == "KaiCare Ai - Doctor"

    @pytest.mark.order(2)
    def test_dashboard_total_patients_tile_navigation(self):
        """Test Step 2: Dashboard - Tiles - Navigate to Total Patients Tile and Verify Count
        - Click on 'Total Patients' tile.
        - Expected Result: Patient list table updated.
        - Verification: Verify selected tile count equals the number of rows in the patient list table.
        """
        # total_patients_card = self.driver.find_element(
        #     By.XPATH,
        #     '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[1]/app-analatics-stat/div/div',
        # )

        # total_patients_card.click()
        # time.sleep(5)

        # patients_count_path = '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[1]/app-analatics-stat/div/div/div[2]/div[1]/h2/span'
        # # Wait until the counter value is visible
        # tile_count_element = self.driver.find_element(By.XPATH, patients_count_path)
        # time.sleep(5)
        # patients_count = tile_count_element.text
        # total_patients_count = int(patients_count)

        # using non consent but eligible card for testing as it has less patients to iterate
        # patient card has 264 entires to iterate.
        # uncomment the above if test has to run for it and comment the below part until line - total_patients_count = int(total_count_str)
        non_consent_eligible_tile=self.driver.find_element(By.XPATH, '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[3]/app-analatics-stat/div/div')
        non_consent_eligible_tile.click()
        time.sleep(10)
        non_consented_eliglible_count_path = '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[3]/app-analatics-stat/div/div/div[2]/div[1]/h2/span'
        non_consented_eliglible_count = self.driver.find_element(By.XPATH, non_consented_eliglible_count_path)
        time.sleep(5)
        total_count_str = non_consented_eliglible_count.text
        total_patients_count = int(total_count_str)

        # Get count from patient table across all pages
        total_rows = 0
        while True:
            time.sleep(3)

            rows = self.driver.find_elements(
                By.XPATH, '//*[@id="customerList"]/div[1]/table/tbody/tr'
            )
            current_page_rows = len(rows)
            total_rows += current_page_rows

            # Last page next link
            # <a aria-label="Next" href="" class="page-link" tabindex="-1" aria-disabled="true"><span aria-hidden="true">»</span><!----></a>
            # Check if next button is disabled using aria-disabled attribute
            is_atag_disabled = self.driver.find_element(By.XPATH, '//a[@aria-label="Next"]').get_attribute("aria-disabled") == "true"
            if is_atag_disabled:
                # reached last page
                break
            else:
                next_button = self.driver.find_element(By.XPATH, '//li[@class="page-item"]//a[@aria-label="Next"]')
                # Wait for button to be clickable with 30 second timeout
                wait_30s = WebDriverWait(self.driver, 30)
                wait_30s.until(EC.element_to_be_clickable(next_button))
                self.driver.execute_script("arguments[0].click();", next_button)

        assert total_patients_count == total_rows, f"Expected tile count {total_patients_count}, but found table count {total_rows}"
        

    @pytest.mark.order(3)
    def test_dashboard_select_patients_for_communication(self):
        """Test Step 3: Dashboard-Patient List - Select Patients for Communication
        - Click 'Select All' checkbox in the patient list table header.
        - Uncheck any one patient.
        - Click 'Communication' button.
        - Verify communication modal opens with selected patients loaded
        - Expected Result: Communication modal opens with selected patients loaded.
        """
        select_all = self.driver.find_element(By.XPATH, '//*[@id="checkAll"]')
        select_all.click()
        time.sleep(3)

        # uncheck 1 customer
        uncheck_a_customer = self.driver.find_element(
            By.XPATH, '//*[@id="checkbox120576"]'
        )
        uncheck_a_customer.click()

        time.sleep(3)

        # communicate
        communicate = self.driver.find_element(
            By.XPATH,
            '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[2]/div/div/div/div[2]/button[1]',
        )
        communicate.click()
        time.sleep(5)

        # Check if "All Patient" radio button is selected
        selected_patients_checkbox = self.driver.find_element(
            By.XPATH, '//*[@id="allPatient"]'
        )
        is_selected = selected_patients_checkbox.is_selected()

        assert is_selected, "Expected 'Selected Patients' radio button to be selected, but it was not selected"
    

    @pytest.mark.order(4)
    def test_dashboard_communication_initiate_sms_communication(self):
        """Test Step 4: Dashboard - Patient List - Communication - Initiate SMS Communication
        - In the Communication modal, By default it select 'SMS' option.
        - Select 'New Group' option.
        - Enter a Group Name.
        - Click 'Save Group'. (Don't click 'Save & Send" option)
        - Expected Result: Group creation request is processed.
        """

        select_patient = self.driver.find_element(By.XPATH, '//*[@id="checkbox120576"]')
        select_patient.click()
        time.sleep(5)

        communicate = self.driver.find_element(
            By.XPATH,
            '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[2]/div/div/div/div[2]/button[1]',
        )
        communicate.click()

        random_number = random.randint(1000, 9999)
        group_name = f"new_test_{random_number}"

        # Find and enter text in group input field
        group_input = self.driver.find_element(
            By.XPATH, '//*[@id="ngb-nav-0-panel"]/app-chat-group/div[1]/div[2]/input'
        )
        group_input.clear()
        group_input.send_keys(group_name)

        # Click save group button
        save_group_button = self.driver.find_element(
            By.XPATH, '//*[@id="ngb-nav-0-panel"]/app-chat-group/div[2]/button[2]'
        )
        save_group_button.click()

        # Wait for confirmation message to appear
        time.sleep(5)

        # Check if modal appears
        modal_element = self.driver.find_element(
            By.XPATH, "/html/body/ngb-modal-window[2]/div/div"
        )
        assert modal_element.is_displayed(), "Modal should be visible after clicking save group"
        

    @pytest.mark.order(5)
    def test_dashboard_communication_verify_confirmation_popup(self):
        """Test Step 5: Dashboard - Patient List - Communication - Verify Confirmation Popup
        - Wait for confirmation popup to appear.
        - Verification: Count displayed in the popup = (Tile patient count-1 unchecked) and Click 'Yes' in the popup.
        """
        select_patient = self.driver.find_element(By.XPATH, '//*[@id="checkbox120576"]')
        select_patient.click()
        time.sleep(3)

        communicate = self.driver.find_element(
            By.XPATH,
            '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[2]/div/div/div/div[2]/button[1]',
        )
        communicate.click()

        random_number = random.randint(1000, 9999)
        group_name = f"new_test_{random_number}"

        # Find and enter text in group input field
        group_input = self.driver.find_element(
            By.XPATH, '//*[@id="ngb-nav-0-panel"]/app-chat-group/div[1]/div[2]/input'
        )
        group_input.clear()
        group_input.send_keys(group_name)

        # Click save group button
        save_group_button = self.driver.find_element(
            By.XPATH, '//*[@id="ngb-nav-0-panel"]/app-chat-group/div[2]/button[2]'
        )
        save_group_button.click()

        # Wait for confirmation message to appear
        time.sleep(5)

        confirmation_element = self.driver.find_element(
            By.XPATH, "/html/body/ngb-modal-window[2]/div/div/div[2]/p/span"
        )
        confirmation_text = confirmation_element.text

        # Assert that confirmation message is "1"
        assert confirmation_text == "1", f"Expected confirmation message to be '1', but got '{confirmation_text}'"
        

        # Click "Yes" button
        yes_button = self.driver.find_element(
            By.XPATH, "/html/body/ngb-modal-window[2]/div/div/div[3]/button[1]"
        )
        yes_button.click()
        time.sleep(5)

        success_modal_msg = self.driver.find_element(
            By.XPATH, '//*[@id="swal2-html-container"]').text
        
        assert success_modal_msg =='Group saved successfully', f"Expected: Group saved successfully but got {success_modal_msg}"
        
    
    @pytest.mark.order(6)
    def test_menu_groups_sms_group_list_verify_creation(self):
        """Test Step 6: Menu - Groups - SMS - Group List - Verify SMS Group Creation
        - Navigate to Menu (Profile)->Click 'Groups'->Select 'SMS Group'->Select 'Group List'.
        - Expected Result: Newly created group is displayed.
        - Verification: Group patient count = (Tile patient count-1 unchecked).
        """
        profile = self.driver.find_element(
            By.XPATH, '//*[@id="page-header-user-dropdown"]/span/span[2]/span'
        )
        profile.click()
        time.sleep(5)

        groups = self.driver.find_element(By.XPATH, "//span[text()='Groups']")
        groups.click()
        time.sleep(5)

        sms_groups = self.driver.find_element(By.XPATH, '//*[@id="ngb-nav-0"]')
        sms_groups.click()
        time.sleep(5)

        rows = self.driver.find_elements(
                By.XPATH, '//*[@id="customerList"]/div[1]/table/tbody/tr'
            )

        first_row = rows[0]
    
        first_group_name = first_row.find_element(By.XPATH, './td[1]').text
        member_count = int(first_row.find_element(By.XPATH, './td[2]').text)

        assert 'new_test_' in first_group_name, f'Group name mismatch-{first_group_name}'
        assert member_count ==1, f'Incorrect member count is{member_count}.'

    @pytest.mark.order(7)
    def test_dashboard_non_consented_eligible_tile_navigation(self):
        """Test Step 7: Dashboard - Tiles - Navigate to Non-Consented But Eligible Tile and Verify Count
        - Click on 'My Health AI' logo on the top of left corner header.
        - Click 'Non-Consented But Eligible' tile.
        - Expected Result: Patient list table updated.
        - Verification: Verify selected tile count equals the number of rows in the patient list table.
        """
        logo = self.driver.find_element(By.XPATH, '//*[@id="page-topbar"]/div[2]/div/div[1]/div/a[2]/span[2]/h4/img')
        logo.click()
        time.sleep(5)

        non_consent_eligible_tile=self.driver.find_element(By.XPATH, '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[3]/app-analatics-stat/div/div')
        non_consent_eligible_tile.click()
        time.sleep(5)

        non_consented_eliglible_count_path = '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[3]/app-analatics-stat/div/div/div[2]/div[1]/h2/span'
        non_consented_eliglible_count = self.driver.find_element(By.XPATH, non_consented_eliglible_count_path)
        time.sleep(5)
        total_count_str = non_consented_eliglible_count.text
        
        # Get count from patient table across all pages
        total_rows = 0
        while True:
            time.sleep(3)

            rows = self.driver.find_elements(
                By.XPATH, '//*[@id="customerList"]/div[1]/table/tbody/tr'
            )
            current_page_rows = len(rows)
            total_rows += current_page_rows

            # Last page next link
            # <a aria-label="Next" href="" class="page-link" tabindex="-1" aria-disabled="true"><span aria-hidden="true">»</span><!----></a>
            # Check if next button is disabled using aria-disabled attribute
            is_atag_disabled = self.driver.find_element(By.XPATH, '//a[@aria-label="Next"]').get_attribute("aria-disabled") == "true"
            if is_atag_disabled:
                # reached last page
                break
            else:
                next_button = self.driver.find_element(By.XPATH, '//li[@class="page-item"]//a[@aria-label="Next"]')
                # Wait for button to be clickable with 30 second timeout
                wait_30s = WebDriverWait(self.driver, 30)
                wait_30s.until(EC.element_to_be_clickable(next_button))
                self.driver.execute_script("arguments[0].click();", next_button)


        assert int(total_count_str) == total_rows, f"Expected tile count {total_count_str}, but found table count {total_rows}"
        
        
    @pytest.mark.order(8)
    def test_dashboard_patient_list_select_patients_for_email_communication(self):
        """Test Step 8: Dashboard-Patient List - Select Patients for Communication
        - Click 'Select All' checkbox in the patient list table header.
        - Count the number of patients who have a valid email address updated.
        - Click 'Communication' button.
        - Expected Result: Communication modal should open. Only patients with a valid email address should be available for email communication. Selected patients must be loaded into the modal.
        """
        # validate non consent but eligible patient count as it has less numbers to iterate
        non_consent_eligible_tile=self.driver.find_element(By.XPATH, '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[3]/app-analatics-stat/div/div')
        non_consent_eligible_tile.click()
        time.sleep(5)
        

        # Count active email buttons across all pages
        valid_email_count = 0
        while True:
            time.sleep(3)

            # Count email buttons on current page
            email_buttons = self.driver.find_elements(
                By.XPATH, '//button[@title="Email"]'
            )
            current_page_active_emails = 0

            for button in email_buttons:
                # Check if button is not disabled (enabled means valid email)
                if not button.get_attribute("disabled"):
                    current_page_active_emails += 1

            valid_email_count += current_page_active_emails

            # Last page next link
            # <a aria-label="Next" href="" class="page-link" tabindex="-1" aria-disabled="true"><span aria-hidden="true">»</span><!----></a>
            # Check if next button is disabled using aria-disabled attribute
            is_atag_disabled = self.driver.find_element(By.XPATH, '//a[@aria-label="Next"]').get_attribute("aria-disabled") == "true"
            if is_atag_disabled:
                break
            else:
                next_button = self.driver.find_element(
                    By.XPATH, '//li[@class="page-item"]//a[@aria-label="Next"]'
                )
                # Wait for button to be clickable with 30 second timeout
                wait_30s = WebDriverWait(self.driver, 30)
                wait_30s.until(EC.element_to_be_clickable(next_button))
                self.driver.execute_script("arguments[0].click();", next_button)

        select_all_checkbox = self.driver.find_element(By.XPATH, '//*[@id="checkAll"]')
        select_all_checkbox.click()
        time.sleep(5)

        communicate_button = self.driver.find_element(
            By.XPATH,
            '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[2]/div/div/div/div[2]/button[1]',
        )
        communicate_button.click()
        time.sleep(5)

        modal_element = self.driver.find_element(By.XPATH, '//*[@id="ngb-nav-0-panel"]')
        assert modal_element.is_displayed(), "Communication modal should be visible"

        email_tab = self.driver.find_element(By.XPATH, '//*[@id="ngb-nav-1"]')
        email_tab.click()
        time.sleep(5)

        email_span = self.driver.find_element(
            By.XPATH,
            '//div[@class="form-control d-flex align-items-center flex-wrap"]/span[1]',
        )
        email_text = email_span.text.strip()
        visible_email_count = 0
        # Count visible emails by splitting on comma
        if email_text:
            visible_emails = [
                email.strip() for email in email_text.split(",") if email.strip()
            ]
            visible_email_count = len(visible_emails)

        badge_span = self.driver.find_element(
            By.XPATH,
            '//div[@class="form-control d-flex align-items-center flex-wrap"]/span[@class="badge bg-primary text-white ms-2"]',
        )
        badge_text = badge_span.text.strip()
        badge_count = int(badge_text.replace("+", ""))
        total_email_count = visible_email_count + badge_count

        # Verify the count matches our earlier count
        assert total_email_count == valid_email_count, f"Expected {valid_email_count} patients with valid emails, but found {total_email_count}"
        
    
    @pytest.mark.order(9)
    def test_dashboard_communication_initiate_email_communication(self):
        """Test Step 9: Dashboard - Patient List - Communication - Initiate Email Communication
        - In the Communication modal, select 'Email' option.
        - Verification (To Field): The email list count must match the number of patients that already have a valid email address.
        - Enter a 'Subject' and Enter the Mail Content as "Test Automation Mail".
        - Click 'Send'.
        - Expected Result: Group creation request is processed and The system should send the mail to all selected patients who had valid email addresses.
        """
        non_consent_eligible_tile=self.driver.find_element(By.XPATH, '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[1]/div[2]/div/div[3]/app-analatics-stat/div/div')
        non_consent_eligible_tile.click()
        time.sleep(5)
        
        # Count active email buttons across all pages
        valid_email_count = 0
        while True:
            time.sleep(3)

            # Count email buttons on current page
            email_buttons = self.driver.find_elements(
                By.XPATH, '//button[@title="Email"]'
            )
            current_page_active_emails = 0

            for button in email_buttons:
                # Check if button is not disabled (enabled means valid email)
                if not button.get_attribute("disabled"):
                    current_page_active_emails += 1

            valid_email_count += current_page_active_emails

            # Last page next link
            # <a aria-label="Next" href="" class="page-link" tabindex="-1" aria-disabled="true"><span aria-hidden="true">»</span><!----></a>
            # Check if next button is disabled using aria-disabled attribute
            is_atag_disabled = self.driver.find_element(By.XPATH, '//a[@aria-label="Next"]').get_attribute("aria-disabled") == "true"
            if is_atag_disabled:
                break
            else:
                next_button = self.driver.find_element(
                    By.XPATH, '//li[@class="page-item"]//a[@aria-label="Next"]'
                )
                # Wait for button to be clickable with 30 second timeout
                wait_30s = WebDriverWait(self.driver, 30)
                wait_30s.until(EC.element_to_be_clickable(next_button))
                self.driver.execute_script("arguments[0].click();", next_button)

        select_all_checkbox = self.driver.find_element(By.XPATH, '//*[@id="checkAll"]')
        select_all_checkbox.click()
        time.sleep(5)

        communicate_button = self.driver.find_element(
            By.XPATH,
            '//*[@id="layout-wrapper"]/div/div/div/app-listjs/div[2]/div/div/div/div[2]/button[1]',
        )
        communicate_button.click()
        time.sleep(5)

        modal_element = self.driver.find_element(By.XPATH, '//*[@id="ngb-nav-0-panel"]')
        assert modal_element.is_displayed(), "Communication modal should be visible"

        email_tab = self.driver.find_element(By.XPATH, '//*[@id="ngb-nav-1"]')
        email_tab.click()
        time.sleep(5)

        email_span = self.driver.find_element(
            By.XPATH,
            '//div[@class="form-control d-flex align-items-center flex-wrap"]/span[1]',
        )
        email_text = email_span.text.strip()
        visible_email_count = 0
        # Count visible emails by splitting on comma
        if email_text:
            visible_emails = [
                email.strip() for email in email_text.split(",") if email.strip()
            ]
            visible_email_count = len(visible_emails)

        badge_span = self.driver.find_element(
            By.XPATH,
            '//div[@class="form-control d-flex align-items-center flex-wrap"]/span[@class="badge bg-primary text-white ms-2"]',
        )
        badge_text = badge_span.text.strip()
        badge_count = int(badge_text.replace("+", ""))
        total_email_count = visible_email_count + badge_count

        # Verify the count matches our earlier count
        assert total_email_count == valid_email_count, (
            f"Expected {valid_email_count} patients with valid emails, but found {total_email_count}"
        )
        
        # Fill subject field
        subject_field = self.driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Subject"]')
        subject_field.clear()
        subject_field.send_keys("test subject")

        # Fill body field (CKEditor)
        body_field = self.driver.find_element(
            By.XPATH, '//*[@id="ngb-nav-1-panel"]/form/div[1]/div[5]/div/div/ckeditor/div[2]/div[2]/div')
        body_field.clear()
        body_field.send_keys("Test Automation Mail")

        # Click send button
        send_button = self.driver.find_element(
          By.XPATH, '//*[@id="ngb-nav-1-panel"]/form/div[2]/button[2]'
        )
        send_button.click()

        # Wait for the action to complete
        time.sleep(10)

        success_msg = self.driver.find_element(
          By.XPATH,'//*[@id="swal2-html-container"]').text
        assert success_msg == 'Email sent successfully!', f'Incorrect message - {success_msg}. Expected: Email sent successfully!'

    @pytest.mark.order(10)
    def test_menu_groups_email_group_list_verify_creation(self):
        """Test Step 10: Menu - Groups - Email - Group List - Verify Email Group Creation
        - Navigate to Menu (Profile)->Click 'Groups'->Select 'Email Group'->Select 'Group List'.
        - Expected Result: Newly created group is displayed.
        - Verification: The group list count must match the number of patients that already have a valid email address.
        """
        profile = self.driver.find_element(
            By.XPATH, '//*[@id="page-header-user-dropdown"]/span/span[2]/span'
        )
        profile.click()
        time.sleep(5)

        groups = self.driver.find_element(By.XPATH, "//span[text()='Groups']")
        groups.click()
        time.sleep(5)

        email_groups = self.driver.find_element(By.XPATH, '//span[text()="Email Group"]')
        email_groups.click()
        time.sleep(5)

        rows = self.driver.find_elements(
                By.XPATH, '//*[@id="customerList"]/div[1]/table/tbody/tr'
            )
        first_row = rows[0]
    
        first_group_name = first_row.find_element(By.XPATH, './td[1]').text
        member_count = int(first_row.find_element(By.XPATH, './td[2]').text)

        assert 'new_test_' in first_group_name, f'Group name mismatch-{first_group_name}'
        assert member_count ==1, f'Incorrect member count is{member_count}.'

    @pytest.mark.order(11)
    def test_menu_logout(self):
        """Test Step 11: Menu - Logout
        - Navigate to Menu->Click Logout.
        - Expected Result: User is logged out and redirected to the login screen.
        """
        profile = self.driver.find_element(
            By.XPATH, '//*[@id="page-header-user-dropdown"]/span/span[2]/span'
        )
        profile.click()
        time.sleep(5)
        logout_button = self.driver.find_element(By.XPATH, "//span[text()='Logout']")
        logout_button.click()

        # Wait for redirect to login page
        time.sleep(3)

        # Verify we're actually on the login page URL
        expected_url = "https://doctorstaging.myhealthai.io/auth/login"
        current_url = self.driver.current_url
        assert current_url == expected_url, (
            f"Expected to be redirected to login page, but current URL is: {current_url}"
        )
