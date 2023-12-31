# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class AccountDetailsRequestAccountInfo(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, account_type: str=None, account_number: str=None, card_number: str=None):  # noqa: E501
        """AccountDetailsRequestAccountInfo - a model defined in Swagger

        :param account_type: The account_type of this AccountDetailsRequestAccountInfo.  # noqa: E501
        :type account_type: str
        :param account_number: The account_number of this AccountDetailsRequestAccountInfo.  # noqa: E501
        :type account_number: str
        :param card_number: The card_number of this AccountDetailsRequestAccountInfo.  # noqa: E501
        :type card_number: str
        """
        self.swagger_types = {
            'account_type': str,
            'account_number': str,
            'card_number': str
        }

        self.attribute_map = {
            'account_type': 'accountType',
            'account_number': 'accountNumber',
            'card_number': 'cardNumber'
        }
        self._account_type = account_type
        self._account_number = account_number
        self._card_number = card_number

    @classmethod
    def from_dict(cls, dikt) -> 'AccountDetailsRequestAccountInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The accountDetailsRequest_accountInfo of this AccountDetailsRequestAccountInfo.  # noqa: E501
        :rtype: AccountDetailsRequestAccountInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def account_type(self) -> str:
        """Gets the account_type of this AccountDetailsRequestAccountInfo.


        :return: The account_type of this AccountDetailsRequestAccountInfo.
        :rtype: str
        """
        return self._account_type

    @account_type.setter
    def account_type(self, account_type: str):
        """Sets the account_type of this AccountDetailsRequestAccountInfo.


        :param account_type: The account_type of this AccountDetailsRequestAccountInfo.
        :type account_type: str
        """

        self._account_type = account_type

    @property
    def account_number(self) -> str:
        """Gets the account_number of this AccountDetailsRequestAccountInfo.


        :return: The account_number of this AccountDetailsRequestAccountInfo.
        :rtype: str
        """
        return self._account_number

    @account_number.setter
    def account_number(self, account_number: str):
        """Sets the account_number of this AccountDetailsRequestAccountInfo.


        :param account_number: The account_number of this AccountDetailsRequestAccountInfo.
        :type account_number: str
        """

        self._account_number = account_number

    @property
    def card_number(self) -> str:
        """Gets the card_number of this AccountDetailsRequestAccountInfo.


        :return: The card_number of this AccountDetailsRequestAccountInfo.
        :rtype: str
        """
        return self._card_number

    @card_number.setter
    def card_number(self, card_number: str):
        """Sets the card_number of this AccountDetailsRequestAccountInfo.


        :param card_number: The card_number of this AccountDetailsRequestAccountInfo.
        :type card_number: str
        """

        self._card_number = card_number
