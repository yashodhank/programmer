# -*- coding: utf-8 -*-
from lettuce import step, world, before
from salad.logger import logger

@step(r"go to the home page")
def go_to_home(step):
    step.given('I visit the url "http://localhost:8000"')

@step(r'I am logged in as "([^"]*)" using "([^"])"')
def is_logged_in(step, user, pwd):
    step.behave_as(
        """
        Given I go to the home page
            And I click on the link with the text "Login"
            And I wait 1 second
            And I click on the field with the id "login_email"
            And I fill in the field with id "login_email" with "{user}"
            And I click on the field with the id "login_password"
            And I fill in the field with id "login_password" with "{pwd}"
            And I click the button with the css selector ".btn-login"
            And I wait 2 seconds
        """.format(user=user, pwd=pwd)
    )

@step(u"go to the desk")
def go_to_desk(step):
    step.given('I click on the element with the css selector ".navbar-home"')

@step('select the option "([^"]*)" in the field "([^"]*)"')
def select_frappe_field(step, option, selector):
    step.behave_as("""
        Given I scroll to "{selector}"
            And I click on the element with the xpath "{option}"
            And I hit the ESCAPE key
    """.format(selector="select[data-fieldname='{}']".format(selector), 
                option="//option[@value='{}']".format(option)))

@step(u'fill the field "([^"]*)" with "([^"]*)"')
def fill_frappe_field(step, selector, value):
    step.behave_as("""
        Given I scroll to "{selector}" 
            And I click on the field with the css selector "{selector}"
            And I fill in the field with the css selector "{selector}" with "{value}"
    """.format(selector="input[data-fieldname='{}']".format(selector), value=value))

@step(u'check the field "([^"]*)"')
def check_frappe_field(step, selector):
    step.given('I click on the field with the css selector "selector"'.format(
        selector="input[data-fieldname='{}']".format(selector)
    ))

@step(u'turn (on|off) the field "([^"]*)"')
def turn_to_frappe(step, turn_to, selector):
    step.behave_as()

@step('move to ([Nn]ext|[[Pp]rev]ious)')
def moving(step, move_to):
    page = str(int(world.browser.url[-1],10)+1)
    humanized = page + ('st' if page[-1] == '1' else 'nd' if page[-1] == '2' else 'rd' if page[-1] == '3' else 'th')
    step.given('I click on the {} element with the css selector "a.next-btn.btn.btn-primary.btn-sm"'.format(humanized))

@step('I complete the setup')
def completing_setup(step):
    step.behave_as("""Given I click on the last element with the css selector "a.complete-btn.btn.btn-primary.btn-sm"
        And I wait 30 seconds""")

@step('scroll to "([^"]*)"')
def scroll_to(step, selector):
    try:
        world.browser.execute_script('frappe.ui.scroll("{}");'.format(selector));
    except NotImplementedError:
        logger.info("Attemped to run javascript in javascript-disabled browser. Movin along.")

@step('go to the module "([^"]*)"')
def go_to_module(step, module):
    
    step.behave_as("""
    Given I go to the desk
        And I click on the element with the css selector "{}"
        And I wait for ajax
    """.format(selector))

@step('add a new doc "([^"]*)/([^"]*)"')
def add_new_doc(step, module, doctype):
    pass

@step('add a child on "([^"]*)"')
def add_child(step, table):
    step.behave_as("""
        Given I scrool to "{selector}
            And I click on the element with the css selector "{selector}"
    """.format(selector="[data-fieldname='{}'] .grid-row-open .btn-success".format(table)))

@step('save the child "([^"]*)"')
def save_the_child(step, table):
    selector = '[data-fieldname="{0}"] .grid-row-open .btn-success'.format(table)
    step.given('I click on the element with the css selector "{}"'.format(selector))

@before.each_scenario
def ensure_that_setup_scenario_run_in_setup_wizard(scenario):
    if 'Setup' in scenario.name and not '#setup-wizard' in world.browser.url:
        scenario.steps = []
        logger.info("Attemped to do the setup in a instance with the setup already done. Movin along.")