# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class SavepinreqProfileInfo(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, customer_id: str=None, account_number: str=None, ssn: str=None):  # noqa: E501
        """SavepinreqProfileInfo - a model defined in Swagger

        :param customer_id: The customer_id of this SavepinreqProfileInfo.  # noqa: E501
        :type customer_id: str
        :param account_number: The account_number of this SavepinreqProfileInfo.  # noqa: E501
        :type account_number: str
        :param ssn: The ssn of this SavepinreqProfileInfo.  # noqa: E501
        :type ssn: str
        """
        self.swagger_types = {
            'customer_id': str,
            'account_number': str,
            'ssn': str
        }

        self.attribute_map = {
            'customer_id': 'customerId',
            'account_number': 'accountNumber',
            'ssn': 'ssn'
        }
        self._customer_id = customer_id
        self._account_number = account_number
        self._ssn = ssn

    @classmethod
    def from_dict(cls, dikt) -> 'SavepinreqProfileInfo':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The savepinreq_profileInfo of this SavepinreqProfileInfo.  # noqa: E501
        :rtype: SavepinreqProfileInfo
        """
        return util.deserialize_model(dikt, cls)

    @property
    def customer_id(self) -> str:
        """Gets the customer_id of this SavepinreqProfileInfo.


        :return: The customer_id of this SavepinreqProfileInfo.
        :rtype: str
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, customer_id: str):
        """Sets the customer_id of this SavepinreqProfileInfo.


        :param customer_id: The customer_id of this SavepinreqProfileInfo.
        :type customer_id: str
        """

        self._customer_id = customer_id

    @property
    def account_number(self) -> str:
        """Gets the account_number of this SavepinreqProfileInfo.


        :return: The account_number of this SavepinreqProfileInfo.
        :rtype: str
        """
        return self._account_number

    @account_number.setter
    def account_number(self, account_number: str):
        """Sets the account_number of this SavepinreqProfileInfo.


        :param account_number: The account_number of this SavepinreqProfileInfo.
        :type account_number: str
        """

        self._account_number = account_number

    @property
    def ssn(self) -> str:
        """Gets the ssn of this SavepinreqProfileInfo.


        :return: The ssn of this SavepinreqProfileInfo.
        :rtype: str
        """
        return self._ssn

    @ssn.setter
    def ssn(self, ssn: str):
        """Sets the ssn of this SavepinreqProfileInfo.


        :param ssn: The ssn of this SavepinreqProfileInfo.
        :type ssn: str
        """

        self._ssn = ssn
