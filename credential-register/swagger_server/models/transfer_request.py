# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class TransferRequest(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, customer_id: float=None, amount: float=None, currency: str=None, source_account_id: str=None, target_account_id: str=None, _date: str=None, description: str=None, transaction_type: str=None, payment_type: str=None):  # noqa: E501
        """TransferRequest - a model defined in Swagger

        :param customer_id: The customer_id of this TransferRequest.  # noqa: E501
        :type customer_id: float
        :param amount: The amount of this TransferRequest.  # noqa: E501
        :type amount: float
        :param currency: The currency of this TransferRequest.  # noqa: E501
        :type currency: str
        :param source_account_id: The source_account_id of this TransferRequest.  # noqa: E501
        :type source_account_id: str
        :param target_account_id: The target_account_id of this TransferRequest.  # noqa: E501
        :type target_account_id: str
        :param _date: The _date of this TransferRequest.  # noqa: E501
        :type _date: str
        :param description: The description of this TransferRequest.  # noqa: E501
        :type description: str
        :param transaction_type: The transaction_type of this TransferRequest.  # noqa: E501
        :type transaction_type: str
        :param payment_type: The payment_type of this TransferRequest.  # noqa: E501
        :type payment_type: str
        """
        self.swagger_types = {
            'customer_id': float,
            'amount': float,
            'currency': str,
            'source_account_id': str,
            'target_account_id': str,
            '_date': str,
            'description': str,
            'transaction_type': str,
            'payment_type': str
        }

        self.attribute_map = {
            'customer_id': 'customerId',
            'amount': 'amount',
            'currency': 'currency',
            'source_account_id': 'sourceAccountId',
            'target_account_id': 'targetAccountId',
            '_date': 'date',
            'description': 'description',
            'transaction_type': 'TransactionType',
            'payment_type': 'PaymentType'
        }
        self._customer_id = customer_id
        self._amount = amount
        self._currency = currency
        self._source_account_id = source_account_id
        self._target_account_id = target_account_id
        self.__date = _date
        self._description = description
        self._transaction_type = transaction_type
        self._payment_type = payment_type

    @classmethod
    def from_dict(cls, dikt) -> 'TransferRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The transferRequest of this TransferRequest.  # noqa: E501
        :rtype: TransferRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def customer_id(self) -> float:
        """Gets the customer_id of this TransferRequest.


        :return: The customer_id of this TransferRequest.
        :rtype: float
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, customer_id: float):
        """Sets the customer_id of this TransferRequest.


        :param customer_id: The customer_id of this TransferRequest.
        :type customer_id: float
        """
        if customer_id is None:
            raise ValueError("Invalid value for `customer_id`, must not be `None`")  # noqa: E501

        self._customer_id = customer_id

    @property
    def amount(self) -> float:
        """Gets the amount of this TransferRequest.


        :return: The amount of this TransferRequest.
        :rtype: float
        """
        return self._amount

    @amount.setter
    def amount(self, amount: float):
        """Sets the amount of this TransferRequest.


        :param amount: The amount of this TransferRequest.
        :type amount: float
        """
        if amount is None:
            raise ValueError("Invalid value for `amount`, must not be `None`")  # noqa: E501

        self._amount = amount

    @property
    def currency(self) -> str:
        """Gets the currency of this TransferRequest.


        :return: The currency of this TransferRequest.
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency: str):
        """Sets the currency of this TransferRequest.


        :param currency: The currency of this TransferRequest.
        :type currency: str
        """
        if currency is None:
            raise ValueError("Invalid value for `currency`, must not be `None`")  # noqa: E501

        self._currency = currency

    @property
    def source_account_id(self) -> str:
        """Gets the source_account_id of this TransferRequest.


        :return: The source_account_id of this TransferRequest.
        :rtype: str
        """
        return self._source_account_id

    @source_account_id.setter
    def source_account_id(self, source_account_id: str):
        """Sets the source_account_id of this TransferRequest.


        :param source_account_id: The source_account_id of this TransferRequest.
        :type source_account_id: str
        """
        if source_account_id is None:
            raise ValueError("Invalid value for `source_account_id`, must not be `None`")  # noqa: E501

        self._source_account_id = source_account_id

    @property
    def target_account_id(self) -> str:
        """Gets the target_account_id of this TransferRequest.


        :return: The target_account_id of this TransferRequest.
        :rtype: str
        """
        return self._target_account_id

    @target_account_id.setter
    def target_account_id(self, target_account_id: str):
        """Sets the target_account_id of this TransferRequest.


        :param target_account_id: The target_account_id of this TransferRequest.
        :type target_account_id: str
        """
        if target_account_id is None:
            raise ValueError("Invalid value for `target_account_id`, must not be `None`")  # noqa: E501

        self._target_account_id = target_account_id

    @property
    def _date(self) -> str:
        """Gets the _date of this TransferRequest.


        :return: The _date of this TransferRequest.
        :rtype: str
        """
        return self.__date

    @_date.setter
    def _date(self, _date: str):
        """Sets the _date of this TransferRequest.


        :param _date: The _date of this TransferRequest.
        :type _date: str
        """
        if _date is None:
            raise ValueError("Invalid value for `_date`, must not be `None`")  # noqa: E501

        self.__date = _date

    @property
    def description(self) -> str:
        """Gets the description of this TransferRequest.

        Loans/Mortgage Payment for loan payments, for internal transfer transaction type and payment type do not exist  # noqa: E501

        :return: The description of this TransferRequest.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this TransferRequest.

        Loans/Mortgage Payment for loan payments, for internal transfer transaction type and payment type do not exist  # noqa: E501

        :param description: The description of this TransferRequest.
        :type description: str
        """

        self._description = description

    @property
    def transaction_type(self) -> str:
        """Gets the transaction_type of this TransferRequest.


        :return: The transaction_type of this TransferRequest.
        :rtype: str
        """
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, transaction_type: str):
        """Sets the transaction_type of this TransferRequest.


        :param transaction_type: The transaction_type of this TransferRequest.
        :type transaction_type: str
        """

        self._transaction_type = transaction_type

    @property
    def payment_type(self) -> str:
        """Gets the payment_type of this TransferRequest.

        it can be minimum or monthly or additional principal payment  # noqa: E501

        :return: The payment_type of this TransferRequest.
        :rtype: str
        """
        return self._payment_type

    @payment_type.setter
    def payment_type(self, payment_type: str):
        """Sets the payment_type of this TransferRequest.

        it can be minimum or monthly or additional principal payment  # noqa: E501

        :param payment_type: The payment_type of this TransferRequest.
        :type payment_type: str
        """

        self._payment_type = payment_type
