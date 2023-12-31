# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class LimitsResponseInnerPurchaseLimitsMonthly(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, available: float=None, maximum: float=None, spent: float=None):  # noqa: E501
        """LimitsResponseInnerPurchaseLimitsMonthly - a model defined in Swagger

        :param available: The available of this LimitsResponseInnerPurchaseLimitsMonthly.  # noqa: E501
        :type available: float
        :param maximum: The maximum of this LimitsResponseInnerPurchaseLimitsMonthly.  # noqa: E501
        :type maximum: float
        :param spent: The spent of this LimitsResponseInnerPurchaseLimitsMonthly.  # noqa: E501
        :type spent: float
        """
        self.swagger_types = {
            'available': float,
            'maximum': float,
            'spent': float
        }

        self.attribute_map = {
            'available': 'available',
            'maximum': 'maximum',
            'spent': 'spent'
        }
        self._available = available
        self._maximum = maximum
        self._spent = spent

    @classmethod
    def from_dict(cls, dikt) -> 'LimitsResponseInnerPurchaseLimitsMonthly':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The limitsResponse_inner_purchase_limits_monthly of this LimitsResponseInnerPurchaseLimitsMonthly.  # noqa: E501
        :rtype: LimitsResponseInnerPurchaseLimitsMonthly
        """
        return util.deserialize_model(dikt, cls)

    @property
    def available(self) -> float:
        """Gets the available of this LimitsResponseInnerPurchaseLimitsMonthly.


        :return: The available of this LimitsResponseInnerPurchaseLimitsMonthly.
        :rtype: float
        """
        return self._available

    @available.setter
    def available(self, available: float):
        """Sets the available of this LimitsResponseInnerPurchaseLimitsMonthly.


        :param available: The available of this LimitsResponseInnerPurchaseLimitsMonthly.
        :type available: float
        """

        self._available = available

    @property
    def maximum(self) -> float:
        """Gets the maximum of this LimitsResponseInnerPurchaseLimitsMonthly.


        :return: The maximum of this LimitsResponseInnerPurchaseLimitsMonthly.
        :rtype: float
        """
        return self._maximum

    @maximum.setter
    def maximum(self, maximum: float):
        """Sets the maximum of this LimitsResponseInnerPurchaseLimitsMonthly.


        :param maximum: The maximum of this LimitsResponseInnerPurchaseLimitsMonthly.
        :type maximum: float
        """

        self._maximum = maximum

    @property
    def spent(self) -> float:
        """Gets the spent of this LimitsResponseInnerPurchaseLimitsMonthly.


        :return: The spent of this LimitsResponseInnerPurchaseLimitsMonthly.
        :rtype: float
        """
        return self._spent

    @spent.setter
    def spent(self, spent: float):
        """Sets the spent of this LimitsResponseInnerPurchaseLimitsMonthly.


        :param spent: The spent of this LimitsResponseInnerPurchaseLimitsMonthly.
        :type spent: float
        """

        self._spent = spent
