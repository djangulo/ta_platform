from selenium import webdriver
import unittest

browser = webdriver.Firefox()

class NewApplicantTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
    
    def tearDown(self):
        self.browser.quit()

    def test_can_view_application_frorm(self):
        # David has just heard about this new company that he can 
        # apply to. So he tries to check out its homepage
        self.browser.get('http://localhost:8000')

        # He notices the page title and header mention 'Apply now!'
        self.assertIn('Apply', self.browser.title)
        self.fail('Finish me!')

    # He is immediately presented with an application form

    # They ask his information in different levels:

    # First, it's personal information, like national ID, phone numbers,
    # email, first & last name, address and gender

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


if __name__ == '__main__':
    unittest.main(warnings='ignore')
