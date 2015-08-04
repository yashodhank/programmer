Feature: Ensuring that the instance works, and the UI loads fine
In order to make sure that ERPNext works
As a User doing your first login
I open the Instance URL using salad

    Scenario: First Login
        Given I am logged in as "Administrator" passing "admin"
        When I look around
        Then I should see "ERPNext" anywhere in the page

    Scenario: Instance Setup - Step 1 [The Language]
        Given I look around
        When I select the option "english" in the field "language" 
            And I move to next
        Then I should see "Region" somewhere in the page

    Scenario: Instance Setup - Step 2 [The Location]
        Given I look around
        When I select the option "United States" in the field "country"
            And I select the option "America/New_York" in the field "timezone"
            And I select the option "USD" in the field "currency"
            And I move to next
        Then I should see "The First User: You" somewhere in the page

    Scenario: Instance Setup - Step 3 [System Admin]
        Given I look around
        When I fill the field "first_name" with "Test"
            And I fill the field "last_name" with "User"
            And I fill the field "email" with "test_demo@our_company.com"
            And I fill the field "password" with "test"
            And I move to next
        Then I should see "The Organization" somewhere in the page

    Scenario: Instance Setup - Step 4 [The Organization]
        Given I look around
        When I fill the field "company_name" with "Wind Power LLC"
            And I fill the field "company_abbr" with "WPL"
            And I fill the field "company_tagline" with "Wind Mills for a Better Tomorrow"
            And I fill the field "bank_account" with "Citibank"
            And I select the option "Standard" in the field "chart_of_accounts"
            And I fill the field "fy_start_date" with "01-01-2015"
            And I fill the field "fy_end_date" with "12-31-2015"
            And I move to next
        Then I should see "The Brand" somewhere in the page

    Scenario: Instance Setup - Step 5 [The Brand]
        Given I look around 
        When I move to next
        Then I should see "Add Users" somewhere in the page

    Scenario: Instance Setup - Step 6 [The Users]
        Given I look around
        When I move to next
        Then I should see "Add Taxes" somewhere in the page

    Scenario: Instance Setup - Step 7 [The Taxes]
        Given I look around
        When I move to next
        Then I should see "Your Customers" somewhere in the page

    Scenario: Instance Setup - Setup 8 [The Customers]
        Given I look around
        When I fill the field "customer_1" with "Standard Customer"
            And I move to next
        Then I should see "Your Suppliers" somewhere in the page

    Scenario: Instance Setup - Setup 9 [The Supplier]
        Given I look around
        When I fill the field "supplier_1" with "Standard Supplier"
            And I move to next
        The I should see "Your Products or Services" somewhere in the page

    Scenario: Instance Setup - Setup 10 [The Products or Services]
        Given I look around
        When I fill the field "item_1" with "Standard Product"
            And I complete the setup
        Then should see "Test User" somewhere in the page