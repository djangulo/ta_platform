from selenium.webdriver.common.keys import Keys
from selenium import webdriver

from .base import FunctionalTest


# John heard of the external referral program, so he
# wants to refer, even though he does not working for
# the company, so he:
class RegistrationProcessTest(FunctionalTest):

    def test_can_open_home_page(self):
        # Opens the company website link
        self.browser.get(self.live_server_url)

        # He notices the page title and header mention 'Home'
        self.assertIn('Home', self.browser.title)

    def test_sign_up_link_redirects(self):
        pass
        # He then looks for the 'Register' button
        self.browser.get(self.live_server_url)
        sign_up = self.browser.find_element_by_link_text('Register')
        # and clicks it
        sign_up.click()
        # he then notices the header reads "Register"
        self.assertIn('Register', self.browser.title)


# John heard of the external referral program, so he
# wants to refer, even though he does not working for
# the company, so he:

# registers for an account

# receives a confirmation email

# clicks the confirmation email link

# the email link takes him to a profile completion page

# once his profile is complete, he can refer!