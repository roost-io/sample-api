# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.get_account_data_accounts_card_restrictions_countries import GetAccountDataAccountsCardRestrictionsCountries  # noqa: F401,E501
from swagger_server.models.get_account_data_accounts_card_restrictions_mcc import GetAccountDataAccountsCardRestrictionsMCC  # noqa: F401,E501
from swagger_server import util


class GetAccountDataAccountsCardRestrictions(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, countries: List[GetAccountDataAccountsCardRestrictionsCountries]=None, mcc: List[GetAccountDataAccountsCardRestrictionsMCC]=None):  # noqa: E501
        """GetAccountDataAccountsCardRestrictions - a model defined in Swagger

        :param countries: The countries of this GetAccountDataAccountsCardRestrictions.  # noqa: E501
        :type countries: List[GetAccountDataAccountsCardRestrictionsCountries]
        :param mcc: The mcc of this GetAccountDataAccountsCardRestrictions.  # noqa: E501
        :type mcc: List[GetAccountDataAccountsCardRestrictionsMCC]
        """
        self.swagger_types = {
            'countries': List[GetAccountDataAccountsCardRestrictionsCountries],
            'mcc': List[GetAccountDataAccountsCardRestrictionsMCC]
        }

        self.attribute_map = {
            'countries': 'countries',
            'mcc': 'MCC'
        }
        self._countries = countries
        self._mcc = mcc

    @classmethod
    def from_dict(cls, dikt) -> 'GetAccountDataAccountsCardRestrictions':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The getAccountData_accounts_cardRestrictions of this GetAccountDataAccountsCardRestrictions.  # noqa: E501
        :rtype: GetAccountDataAccountsCardRestrictions
        """
        return util.deserialize_model(dikt, cls)

    @property
    def countries(self) -> List[GetAccountDataAccountsCardRestrictionsCountries]:
        """Gets the countries of this GetAccountDataAccountsCardRestrictions.


        :return: The countries of this GetAccountDataAccountsCardRestrictions.
        :rtype: List[GetAccountDataAccountsCardRestrictionsCountries]
        """
        return self._countries

    @countries.setter
    def countries(self, countries: List[GetAccountDataAccountsCardRestrictionsCountries]):
        """Sets the countries of this GetAccountDataAccountsCardRestrictions.


        :param countries: The countries of this GetAccountDataAccountsCardRestrictions.
        :type countries: List[GetAccountDataAccountsCardRestrictionsCountries]
        """

        self._countries = countries

    @property
    def mcc(self) -> List[GetAccountDataAccountsCardRestrictionsMCC]:
        """Gets the mcc of this GetAccountDataAccountsCardRestrictions.


        :return: The mcc of this GetAccountDataAccountsCardRestrictions.
        :rtype: List[GetAccountDataAccountsCardRestrictionsMCC]
        """
        return self._mcc

    @mcc.setter
    def mcc(self, mcc: List[GetAccountDataAccountsCardRestrictionsMCC]):
        """Sets the mcc of this GetAccountDataAccountsCardRestrictions.


        :param mcc: The mcc of this GetAccountDataAccountsCardRestrictions.
        :type mcc: List[GetAccountDataAccountsCardRestrictionsMCC]
        """

        self._mcc = mcc
