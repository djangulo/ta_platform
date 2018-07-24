from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from .base import FunctionalTest


class NewApplicantTest(FunctionalTest):

    def test_can_view_application_form(self):
        # David has just heard about this new company that he can 
        # apply to. So he tries to check out its homepage
        self.browser.get(self.live_server_url)

        # He notices the page title and header mention 'Apply now!'
        self.assertIn('Home', self.browser.title)

    def test_title_reads_apply(self):
        # So he clicks it
        self.browser.get(self.live_server_url + '/apply')
        self.assertIn('Apply', self.browser.title)
        # He is immediately presented with an application form

    def test_js_raw_validation(self):
    # They ask his information in different levels:
    # First, it's personal information, like national ID, phone numbers,
    # email, first & last name, address and gender
        self.browser.get(self.live_server_url + '/apply')
        inputbox = self.browser.find_element_by_id(
            'id_application-national_id_number')
        inputbox.send_keys('000-0000000-1')
        submit = self.browser.find_element_by_css_selector(
            'input[type="submit"]')
        submit.click()
        invalid = self.browser.find_element_by_class_name('invalid-feedback')
        self.assertTrue(invalid.get_attribute('visible') == True)



    # He notices that some of the fields are mandatory, and are tagged as 
    # 'required'

    # Then, it asks about his education level, and what institution he 
    # attended

    # After he fills out the forms, he is redirected to a Thank you page,
    # with a message stating that he will be contacted by a recruiter to
    # complete his process

    # Impatiently, he tries to fill a second application, only to find that
    # he cannot apply again: there's a message telling him that his
    # application has already been filed, and that he has to wait 2 months
    # before he can apply again


