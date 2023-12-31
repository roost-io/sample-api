# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.account_details_request_account_info import AccountDetailsRequestAccountInfo  # noqa: F401,E501
from swagger_server import util


class AccountDetailsRequest(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, customer_id: float=None, account_info: List[AccountDetailsRequestAccountInfo]=None):  # noqa: E501
        """AccountDetailsRequest - a model defined in Swagger

        :param customer_id: The customer_id of this AccountDetailsRequest.  # noqa: E501
        :type customer_id: float
        :param account_info: The account_info of this AccountDetailsRequest.  # noqa: E501
        :type account_info: List[AccountDetailsRequestAccountInfo]
        """
        self.swagger_types = {
            'customer_id': float,
            'account_info': List[AccountDetailsRequestAccountInfo]
        }

        self.attribute_map = {
            'customer_id': 'customerId',
            'account_info': 'accountInfo'
        }
        self._customer_id = customer_id
        self._account_info = account_info

    @classmethod
    def from_dict(cls, dikt) -> 'AccountDetailsRequest':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The accountDetailsRequest of this AccountDetailsRequest.  # noqa: E501
        :rtype: AccountDetailsRequest
        """
        return util.deserialize_model(dikt, cls)

    @property
    def customer_id(self) -> float:
        """Gets the customer_id of this AccountDetailsRequest.


        :return: The customer_id of this AccountDetailsRequest.
        :rtype: float
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, customer_id: float):
        """Sets the customer_id of this AccountDetailsRequest.


        :param customer_id: The customer_id of this AccountDetailsRequest.
        :type customer_id: float
        """
        if customer_id is None:
            raise ValueError("Invalid value for `customer_id`, must not be `None`")  # noqa: E501

        self._customer_id = customer_id

    @property
    def account_info(self) -> List[AccountDetailsRequestAccountInfo]:
        """Gets the account_info of this AccountDetailsRequest.


        :return: The account_info of this AccountDetailsRequest.
        :rtype: List[AccountDetailsRequestAccountInfo]
        """
        return self._account_info

    @account_info.setter
    def account_info(self, account_info: List[AccountDetailsRequestAccountInfo]):
        """Sets the account_info of this AccountDetailsRequest.


        :param account_info: The account_info of this AccountDetailsRequest.
        :type account_info: List[AccountDetailsRequestAccountInfo]
        """

        self._account_info = account_info
