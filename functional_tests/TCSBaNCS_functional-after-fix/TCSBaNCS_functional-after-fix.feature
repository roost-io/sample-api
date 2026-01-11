Feature: E-commerce Application Functional Testing

  # UI Test Scenarios
  @ui
  Scenario Outline: User Registration and Account Creation
    Given I am on the registration page
    When I enter valid "<name>", "<email>", and "<password>"
    And I agree to the terms and conditions
    And I click the 'Register' button
    Then a user account is created successfully
    And a confirmation email is sent

    Examples:
      | name     | email           | password   |
      | John Doe | john@example.com| Passw0rd!  |
      | Jane Doe | jane@example.com| Secure123! |

  @ui
  Scenario Outline: Product Search and Filtering
    Given I am on the homepage
    When I enter "<keyword>" in the search bar
    And I apply filters for "<category>" and "<price_range>"
    And I click the 'Search' button
    Then relevant products are displayed according to the search criteria and filters

    Examples:
      | keyword | category | price_range |
      | laptop  | electronics | 500-1000  |
      | shoes   | fashion     | 50-100    |

  @ui
  Scenario Outline: Shopping Cart Management
    Given I am logged in
    And I have selected a product
    When I click 'Add to Cart'
    And I navigate to the cart
    And I remove a product from the cart
    Then the products are added and removed from the cart correctly
    And the cart updates accordingly

    Examples:
      | product_name |
      | Laptop       |
      | Sneakers     |

  @ui
  Scenario Outline: Checkout Process and Payment Integration
    Given I have items in the cart
    When I navigate to checkout
    And I enter "<shipping_details>"
    And I select "<payment_method>"
    And I confirm and complete payment
    Then the order is processed successfully
    And payment is confirmed

    Examples:
      | shipping_details       | payment_method |
      | "123 Main St, City"    | Credit Card    |
      | "456 Elm St, Town"     | PayPal         |

  @ui
  Scenario Outline: Order Confirmation and Receipt Generation
    Given I have completed the checkout process
    When I check for the order confirmation message
    Then the order confirmation is displayed
    And a receipt is generated and emailed to the user

    Examples:
      | order_id |
      | 1001     |
      | 1002     |

  @ui
  Scenario Outline: User Profile Management
    Given I am logged in
    When I navigate to profile settings
    And I update "<field>" to "<new_value>"
    And I save changes
    Then the profile information is updated successfully
    And a confirmation message is displayed

    Examples:
      | field   | new_value       |
      | name    | John Smith      |
      | email   | john.smith@example.com |
      | password| NewPass123!     |

  @ui
  Scenario Outline: Role-based Access Control and Permissions
    Given I log in as a "<user_role>"
    When I attempt to access the admin panel
    Then "<access_result>" is displayed

    Examples:
      | user_role | access_result      |
      | admin     | Access granted     |
      | regular   | Access denied      |

  @ui
  Scenario Outline: Data Validation and Error Handling
    Given I am on a form requiring input validation
    When I enter invalid "<field>" with "<invalid_data>"
    And I submit the form
    Then error messages are displayed for invalid inputs

    Examples:
      | field   | invalid_data |
      | email   | invalidemail |
      | password| short        |

  @ui
  Scenario Outline: UI Interactions across all screens and forms
    Given I access the application on a "<device>"
    When I navigate through various screens and forms
    Then UI elements are responsive and interactive

    Examples:
      | device  |
      | desktop |
      | mobile  |

  @ui
  Scenario Outline: Guest Checkout Process
    Given I have added products to the cart
    When I proceed to checkout as a guest
    And I enter "<shipping_details>" and "<billing_details>"
    And I select "<payment_method>"
    And I complete the payment
    Then the order is processed successfully
    And a confirmation message is displayed

    Examples:
      | shipping_details       | billing_details       | payment_method |
      | "123 Main St, City"    | "123 Main St, City"   | Credit Card    |
      | "456 Elm St, Town"     | "456 Elm St, Town"    | PayPal         |

  @ui
  Scenario Outline: Password Recovery Process
    Given I am on the login page
    When I click on 'Forgot Password'
    And I enter registered email "<email>"
    Then I receive a recovery email
    And I successfully reset the password

    Examples:
      | email            |
      | john@example.com |
      | jane@example.com |

  @ui
  Scenario Outline: Product Review Submission
    Given I am logged in and have purchased the product
    When I navigate to the product page
    And I click on 'Write a Review'
    And I enter review details and rating
    And I submit the review
    Then the review is submitted successfully
    And appears on the product page

    Examples:
      | product_name |
      | Laptop       |
      | Sneakers     |

  @ui
  Scenario Outline: Wishlist Management
    Given I am logged in
    When I navigate to a product page
    And I click 'Add to Wishlist'
    And I navigate to the wishlist
    And I remove a product from the wishlist
    Then the products are added and removed from the wishlist correctly
    And the wishlist updates accordingly

    Examples:
      | product_name |
      | Laptop       |
      | Sneakers     |

  @ui
  Scenario Outline: Multi-Currency Support
    Given the multi-currency feature is enabled
    When I navigate to the currency selection option
    And I select "<currency>"
    And I add products to the cart
    And I proceed to checkout and complete the payment
    Then prices are displayed in the selected currency
    And the transaction is completed successfully

    Examples:
      | currency |
      | USD      |
      | EUR      |
