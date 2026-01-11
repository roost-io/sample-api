Feature: E-commerce Platform Functional Testing

  # UI Test Scenarios
  @ui
  Scenario Outline: User Registration and Account Creation
    Given I am on the registration page
    When I enter valid personal information including name "<name>", email "<email>", and password "<password>"
    And I agree to terms and conditions
    And I click the 'Register' button
    Then a user account is created successfully
    And a confirmation email is sent

    Examples:
      | name   | email            | password  |
      | John   | john@example.com | Pass123!  |
      | Alice  | alice@example.com| Secure456!|

  @ui
  Scenario Outline: Product Search and Filtering
    Given I am logged in and on the homepage
    When I enter "<product_name>" in the search bar
    And I click the 'Search' button
    And I apply filters such as price range "<price_range>" and category "<category>"
    Then search results are displayed according to the search term and applied filters

    Examples:
      | product_name | price_range | category  |
      | Laptop       | $500-$1000  | Electronics|
      | Shoes        | $50-$100    | Fashion   |

  @ui
  Scenario Outline: Checkout Process with Payment Gateway Integration
    Given I have items in the shopping cart
    When I navigate to the shopping cart
    And I click the 'Checkout' button
    And I enter shipping information "<shipping_info>"
    And I select payment method "<payment_method>"
    And I complete payment through the payment gateway
    Then the order is placed successfully
    And payment is processed

    Examples:
      | shipping_info          | payment_method |
      | 123 Main St, City, Zip | Credit Card    |
      | 456 Elm St, City, Zip  | PayPal         |

  @ui
  Scenario Outline: Order Confirmation and Receipt Generation
    Given I have completed a purchase
    When I check my email for order confirmation
    And I view the order receipt in my user account
    Then an order confirmation email is received
    And the receipt is available in the user account

    Examples:
      | email_address       |
      | user1@example.com   |
      | user2@example.com   |

  @ui
  Scenario Outline: Promotional Code Application
    Given I have items in the shopping cart and a valid promotional code "<promo_code>"
    When I navigate to the shopping cart
    And I proceed to checkout
    And I enter the promotional code in the designated field
    And I click 'Apply' button
    Then a discount is applied to the order total
    And it is reflected in the final amount

    Examples:
      | promo_code  |
      | SAVE10      |
      | DISCOUNT20  |

  @ui
  Scenario Outline: Shopping Cart Management
    Given I am logged in and browsing products
    When I add a product "<product>" to the shopping cart
    And I update the quantity of the product in the cart to "<quantity>"
    And I remove a product "<product_to_remove>" from the cart
    Then items are added, updated, and removed from the shopping cart successfully

    Examples:
      | product  | quantity | product_to_remove |
      | Book     | 2        | Book              |
      | Laptop   | 1        | Laptop            |

  @ui
  Scenario Outline: User Profile Management
    Given I am logged in and on the profile page
    When I update personal information fields with name "<name>", email "<email>", and address "<address>"
    And I save changes
    Then profile information is updated successfully
    And changes are reflected immediately

    Examples:
      | name   | email            | address         |
      | John   | john@example.com | 123 Main St     |
      | Alice  | alice@example.com| 456 Elm St      |

  @ui
  Scenario Outline: Product Review and Rating System
    Given I have purchased the product and am logged in
    When I navigate to the purchased product page
    And I enter a review "<review>" in the designated field
    And I select a rating "<rating>"
    And I submit the review and rating
    Then the review and rating are submitted successfully
    And displayed on the product page

    Examples:
      | review          | rating |
      | Great product!  | 5      |
      | Not satisfied   | 2      |

  @ui
  Scenario Outline: Order History and Tracking
    Given I am logged in and have placed orders
    When I navigate to the order history page
    And I select an order to view details
    And I check the tracking status of the order
    Then order history is displayed with accurate details
    And tracking information is up-to-date

    Examples:
      | order_id |
      | 12345    |
      | 67890    |

  @ui
  Scenario Outline: Customer Support Interaction
    Given I am logged in and on the support page
    When I fill out the support request form with details "<details>"
    And I submit the support request
    Then the support request is submitted successfully
    And a confirmation message is displayed

    Examples:
      | details           |
      | Issue with order  |
      | Account question  |

  @ui
  Scenario Outline: Invalid Payment Method Handling
    Given I have items in the shopping cart and an invalid payment method saved
    When I navigate to the shopping cart
    And I click 'Checkout' button
    And I select the invalid payment method
    And I attempt to complete the payment
    Then payment is declined
    And an error message is displayed to the user

    Examples:
      | invalid_method |
      | Expired Card   |
      | Invalid PayPal |

  @ui
  Scenario Outline: Tax and Shipping Fee Calculation
    Given I have items in the shopping cart and am ready to checkout
    When I navigate to the shopping cart
    And I click 'Checkout' button
    And I enter shipping address "<address>"
    And I review the calculated tax and shipping fees
    Then tax and shipping fees are calculated accurately
    And based on the shipping address and order total

    Examples:
      | address          |
      | 123 Main St, Zip |
      | 456 Elm St, Zip  |

  @ui
  Scenario Outline: Expired Promotional Code Handling
    Given I have items in the shopping cart and an expired promotional code "<expired_code>"
    When I navigate to the shopping cart
    And I proceed to checkout
    And I enter the expired promotional code in the designated field
    And I click 'Apply' button
    Then an error message is displayed indicating the promotional code is expired
    And no discount is applied

    Examples:
      | expired_code |
      | OLD10        |
      | EXPIRED20    |

  @ui
  Scenario Outline: Order Status Transition
    Given I have placed an order and am logged in
    When I navigate to the order history page
    And I select the recent order
    And I monitor status changes from pending to confirmed, shipped, and delivered
    Then order status transitions correctly
    And is updated in real-time

    Examples:
      | order_id |
      | 12345    |
      | 67890    |

  @ui
  Scenario Outline: Data Protection Compliance
    Given I am on the registration page
    When I enter personal information including name "<name>", email "<email>", and password "<password>"
    And I review and consent to data protection policies
    And I click 'Register' button
    Then user registration is successful
    And data protection consent is recorded

    Examples:
      | name   | email            | password  |
      | John   | john@example.com | Pass123!  |
      | Alice  | alice@example.com| Secure456!|
