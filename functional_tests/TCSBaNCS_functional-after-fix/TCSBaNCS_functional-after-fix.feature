Feature: E-commerce Platform Functional Testing

  # UI Test Scenarios
  @ui
  Scenario Outline: User Registration and Account Creation
    Given I am on the registration page
    When I enter valid user details including name "<name>", email "<email>", and password "<password>"
    And I agree to terms and conditions
    And I click the 'Register' button
    Then I should receive a confirmation email
    And the account should be created successfully

    Examples:
      | name    | email            | password  |
      | John    | john@example.com | Pass123!  |
      | Alice   | alice@example.com| Pass456!  |

  @ui
  Scenario Outline: Product Search and Filtering
    Given I am on the homepage
    When I enter "<product_name>" in the search bar
    And I apply filters such as price range "<price_range>", category "<category>", and brand "<brand>"
    And I click the 'Search' button
    Then relevant products should be displayed according to the search criteria and filters applied

    Examples:
      | product_name | price_range | category | brand   |
      | Laptop       | 500-1000    | Electronics | Dell  |
      | Shoes        | 50-100      | Fashion     | Nike  |

  @ui
  Scenario Outline: Shopping Cart Management
    Given I am logged in
    And I have added a product "<product>" to the cart
    When I update the quantity of the product to "<quantity>"
    And I remove a product "<product_to_remove>" from the cart
    Then the cart should be updated with correct item quantities and total price

    Examples:
      | product  | quantity | product_to_remove |
      | Laptop   | 2        | Shoes             |
      | Shoes    | 1        | Laptop            |

  @ui
  Scenario Outline: Checkout Process and Payment Gateway Integration
    Given I have items in the cart
    When I proceed to checkout
    And I enter shipping details "<shipping_details>"
    And I select a payment method "<payment_method>"
    And I complete the payment process
    Then payment should be processed successfully
    And an order confirmation should be displayed

    Examples:
      | shipping_details | payment_method |
      | Address1         | Credit Card    |
      | Address2         | PayPal         |

  @ui
  Scenario Outline: Order Confirmation and Notification
    Given I have completed a purchase
    When I check for order confirmation on the website
    And I verify receipt of email notification
    Then order confirmation should be displayed
    And email notification should be received

    Examples:
      | purchase_id |
      | 12345       |
      | 67890       |

  @ui
  Scenario Outline: User Profile Management
    Given I am logged in and on the profile settings page
    When I update profile details including name "<name>", email "<email>", and password "<password>"
    And I save changes
    Then profile information should be updated successfully
    And changes should be reflected in the user account

    Examples:
      | name    | email            | password  |
      | John    | john@example.com | NewPass123! |
      | Alice   | alice@example.com| NewPass456! |

  @ui
  Scenario Outline: Role-based Access Control
    Given I am logged in with a user account assigned a specific role "<role>"
    When I attempt to access various sections of the application
    Then I should be able to access permitted areas
    And I should be restricted from unauthorized sections

    Examples:
      | role      |
      | Admin     |
      | Customer  |

  @ui
  Scenario Outline: Data Validation and Error Handling
    Given I am logged in
    When I navigate to different forms and enter invalid data "<invalid_data>"
    And I submit the form
    Then the system should display appropriate error messages
    And prevent form submission

    Examples:
      | invalid_data          |
      | invalid_email@format  |
      | negative_price        |

  @ui
  Scenario Outline: UI Interactions Across All Screens
    Given I am logged in
    When I navigate through different pages and interact with UI elements
    And I resize the browser window
    Then UI elements should function correctly
    And the layout should be responsive across different screen sizes

    Examples:
      | page      |
      | home      |
      | product   |
      | checkout  |

  @ui
  Scenario Outline: Guest Checkout Process
    Given I have items in the cart
    When I proceed to checkout
    And I select 'Checkout as Guest'
    And I enter shipping details "<shipping_details>"
    And I select a payment method "<payment_method>"
    And I complete the payment process
    Then payment should be processed successfully
    And an order confirmation should be displayed

    Examples:
      | shipping_details | payment_method |
      | Address1         | Credit Card    |
      | Address2         | PayPal         |

  @ui
  Scenario Outline: Wishlist Management
    Given I am logged in
    When I navigate to a product page and add the product "<product>" to the wishlist
    And I view the wishlist
    And I remove a product "<product_to_remove>" from the wishlist
    Then the wishlist should be updated accordingly with correct items

    Examples:
      | product  | product_to_remove |
      | Laptop   | Shoes             |
      | Shoes    | Laptop            |

  @ui
  Scenario Outline: Order History and Details
    Given I am logged in and have completed at least one purchase
    When I navigate to the order history page
    And I select an order "<order_id>" to view details
    Then order history and details should be displayed accurately

    Examples:
      | order_id |
      | 12345    |
      | 67890    |

  @ui
  Scenario Outline: Password Recovery
    Given I have an existing account
    When I navigate to the login page
    And I click on 'Forgot Password'
    And I enter registered email address "<email>"
    And I follow the instructions in the password recovery email
    Then I should be able to reset my password
    And log in with the new password

    Examples:
      | email            |
      | john@example.com |
      | alice@example.com |

  @ui
  Scenario Outline: Multi-Currency Support
    Given I have items in the cart
    When I navigate to the currency selection option
    And I select a different currency "<currency>"
    And I proceed to checkout
    And I complete the payment process
    Then prices should be displayed in the selected currency
    And payment should be processed successfully

    Examples:
      | currency |
      | USD      |
      | EUR      |
