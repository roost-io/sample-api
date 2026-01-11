Feature: E-commerce Platform Functional Testing

  # UI Test Scenarios
  @ui
  Scenario Outline: User Registration with Valid Details
    Given I am on the registration page
    When I enter valid user details including "<name>", "<email>", and "<password>"
    And I click the "Register" button
    Then a user account is created successfully
    And a confirmation email is sent

    Examples:
      | name   | email           | password  |
      | John   | john@example.com| Pass1234  |
      | Alice  | alice@example.com| Pass5678 |

  @ui
  Scenario Outline: Product Search and Filtering
    Given I am on the search page
    When I enter "<keyword>" in the search bar
    And I apply filters such as price range "<price_range>" and category "<category>"
    And I click the "Search" button
    Then relevant products are displayed according to the search criteria and filters

    Examples:
      | keyword | price_range | category  |
      | Laptop  | 500-1000    | Electronics |
      | Shoes   | 50-100      | Fashion     |

  @ui
  Scenario Outline: Shopping Cart Management
    Given I am logged in
    When I search and select a product "<product>"
    And I click "Add to Cart"
    And I navigate to the cart
    And I remove "<product>" from the cart
    Then the product is added and removed from the cart successfully

    Examples:
      | product    |
      | Laptop     |
      | Headphones |

  @ui
  Scenario Outline: Checkout Process
    Given I have items in the cart
    When I click "Checkout"
    And I enter shipping details "<address>", "<city>", "<zip>"
    And I select a payment method "<payment_method>"
    And I complete the payment
    Then the order is placed successfully and payment is processed

    Examples:
      | address       | city     | zip   | payment_method |
      | 123 Main St   | New York | 10001 | Credit Card    |
      | 456 Elm St    | Chicago  | 60601 | PayPal         |

  @ui
  Scenario Outline: Order Confirmation and Notification
    Given I have successfully placed an order
    When I check my email inbox
    Then I receive an order confirmation email with order details

    Examples:
      | email           |
      | john@example.com|
      | alice@example.com|

  @ui
  Scenario Outline: User Profile Management
    Given I am logged in and on the user profile page
    When I edit profile details such as "<name>", "<address>", and "<contact_number>"
    And I click the "Save" button
    Then profile information is updated successfully and changes are reflected immediately

    Examples:
      | name   | address     | contact_number |
      | John   | 123 Main St | 1234567890     |
      | Alice  | 456 Elm St  | 0987654321     |

  @ui
  Scenario Outline: Role-based Access Control
    Given users with different roles exist in the system
    When I log in as "<role>" user
    And I attempt to access "<feature>"
    Then "<accessibility>" access is granted

    Examples:
      | role   | feature          | accessibility |
      | admin  | admin dashboard  | granted       |
      | user   | admin dashboard  | restricted    |

  @ui
  Scenario Outline: Data Validation and Error Handling
    Given I am logged in and on a form requiring data input
    When I enter invalid data "<invalid_data>"
    And I submit the form
    Then appropriate error messages are displayed

    Examples:
      | invalid_data     |
      | invalid-email.com|
      | 123              |

  @ui
  Scenario Outline: UI Interactions Across All Screens
    Given I access the application on "<device>"
    When I perform common actions like navigation and form submissions
    Then UI elements are consistent and functional

    Examples:
      | device  |
      | desktop |
      | mobile  |
      | tablet  |

  @ui
  Scenario Outline: Multi-Device Order Placement
    Given I access the application on "<device>"
    When I add items to the cart and proceed to checkout
    And I complete the order
    Then order placement is successful across all devices with consistent user experience

    Examples:
      | device  |
      | desktop |
      | mobile  |
      | tablet  |

  # API Test Scenarios
  @api
  Scenario Outline: Integration with External Systems
    Given the external inventory system is operational
    When I navigate to a product page
    Then the displayed inventory level matches the external system's inventory data

    Examples:
      | product_id |
      | 101        |
      | 202        |

  @api
  Scenario Outline: Payment Gateway Error Handling
    Given I have items in the cart and a payment method selected
    When I simulate a payment gateway error "<error_type>"
    And I attempt to complete the payment
    Then I receive a clear error message and am prompted to retry or select a different payment method

    Examples:
      | error_type      |
      | network failure |
      | invalid card    |

  @api
  Scenario Outline: Order Status Transition
    Given an order is placed and initially in pending status
    When I confirm the order
    And I ship the order
    Then order status transitions correctly at each step with appropriate notifications

    Examples:
      | order_id |
      | 1001     |
      | 1002     |

  @api
  Scenario Outline: Sensitive Data Masking
    Given I perform actions that involve sensitive data entry
    When I submit the form
    Then sensitive data is masked in logs and partially displayed in UI

    Examples:
      | action         |
      | enter card info|
      | enter password |

  @api
  Scenario Outline: Inventory Update Synchronization
    Given integration with external inventory management system is active
    When I update inventory levels in the external system
    And I navigate to the product page in the application
    Then the displayed inventory matches the updated levels

    Examples:
      | product_id |
      | 303        |
      | 404        |
