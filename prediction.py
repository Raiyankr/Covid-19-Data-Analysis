"""Evaluating the impact of COVID-19 on Canadians’ spending habits: prediction module

This module is responsible for creating a linear regression model with case counts
and spending index data, to make future predictions if there were to be another
pandemic 'wave'.

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Rafael Gacesa.
"""
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


class Predictor:
    """A class representing prediction objects which can make predictions
    based on linear regression models on provided data.
    """
    # Private Instance Attributes:
    #     - _predictor: the sklearn LinearRegression object
    #     - _cases: list of case count data (with number of features)
    #     - _csi: list of csi data corresponding with case counts
    _predictor: LinearRegression
    _cases: list[list]
    _csi: list[float]

    def __init__(self, cases: list, csi: list) -> None:
        """Initialize this predictor with the given data, add number of features
        to case data (1 feature for each case value), and generate the
        LinearRegression object using the generator method."""
        self._cases = [[case, 1] for case in cases]
        self._csi = csi
        self._predictor = self.generate_predictor()

    def generate_predictor(self) -> LinearRegression:
        """Use sklearn LinearRegression objects and data formatting methods to create
        a linear regression prediction object."""
        cases_train, _, csi_train, _ = train_test_split(self._cases, self._csi, random_state=0)
        predictor = LinearRegression()
        predictor.fit(cases_train, csi_train)
        return predictor

    def make_prediction(self, case_count: int) -> float:
        """Use the LinearRegression object to create a prediction based
        on a given case count."""
        return self._predictor.predict([[case_count, 1]])[0]


if __name__ == '__main__':
    import python_ta
    import python_ta.contracts

    python_ta.contracts.check_all_contracts()
    python_ta.check_all(config={
        'extra-imports': ['sklearn.model_selection', 'sklearn.linear_model'],
        'allowed-io': [],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import doctest

    doctest.testmod()
