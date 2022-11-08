"""Evaluating the impact of COVID-19 on Canadians’ spending habits: backend module

This module is responsible for data loading, cleaning, and processing, which includes
calculating metrics that will be plotted using the datasets.

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Rafael Gacesa.
"""
import csv
from dataclasses import dataclass
from datetime import date
from dateutil.relativedelta import relativedelta
from prediction import Predictor


@dataclass
class Month:
    """One month of data from the imported datasets, including calculated metrics

        Instance Attributes:
            - date: a date object representing the date of the data
            - covid_cases: The number of cases recorded in the month
            - unemployment_rate: The unemployment rate during the month
            - baskets: A dictionary containing the weighted percentages of specific commodities
            - cpi: A dictionary containing the relative cost of specific commodities over time
            - csi: A dictionary containing the 'spending index', calculated using cpi and baskets

        Representation Invariants:
            - self.date.month in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}
            - self.date.day == 1
            - self.covid_cases >= 0
            - self.covid_rate >= 0.0
            - self.unemployment_rate >= 0.0
    """
    date: date
    covid_cases: int
    unemployment_rate: float
    baskets: dict
    cpi: dict
    csi: dict


@dataclass
class Basket:
    """A consumer basket which stores the total weight of the basket and its
    sub-categories.

        Instance Attributes:
            - name: the name of the commodity
            - weight: the weight of the basket
            - categories: the sub-categories and their values

        Representation Invariants:
            - value >= 0.0
    """
    name: str
    weight: float
    categories: dict


def load_csv(path: str, headers: bool) -> list[list[str]]:
    """Returns the data contained in a .csv file formatted as a 2D list.
    """
    data = []

    with open(path) as file:
        reader = csv.reader(file, delimiter=',')

        for row in reader:
            data.append(row)

    # removing the headers
    if not headers:
        data.pop(0)

    return data


def load_data(start_date: date, end_date: date, predict: bool = False) -> list[Month]:
    """Returns a list of Month objects from the provided start date to the end date (inclusive).

    The returned list is sorted in ascending order, from earliest to latest.

    Has the bool flag predict for the use of complete_dataset(). By default,
    the data will load in with empty csi dictionaries for months with missing
    basket data. However, when the flag is set to true, a linear regerssion model
    is used to predict the missing values.

    Preconditions:
        - start_date <= end_date

    Sample usage:
    To import data from March 2020 to February 2021:
    >>> start_dt = date(2020, 3, 1)
    >>> end_dt = date(2021, 2, 1)
    >>> loaded_data = load_data(start_dt, end_dt)
    To import data from March 2020 to October 2021,
    filling in missing values with the model:
    >>> start_dt = date(2020, 3, 1)
    >>> end_dt = date(2021, 10, 1)
    >>> loaded_data = load_data(start_dt, end_dt, True)
    """
    raw_data = [load_csv('covid-19_dataset.csv', False),
                load_csv('unemployment-rate_dataset.csv', False),
                load_csv('weighted-baskets_dataset.csv', False),
                load_csv('consumer-price-index_dataset.csv', False)]

    data = []
    rd = relativedelta(end_date, start_date)
    for i in range(rd.months + (rd.years * 12) + 1):
        dt = date((start_date + relativedelta(months=i)).year,
                  (start_date + relativedelta(months=i)).month, 1)

        covid_cases = read_covid_data(raw_data[0], dt)
        unemployment_rate = read_unemployment_data(raw_data[1], dt)
        baskets = read_baskets_data(raw_data[2], dt)
        cpi = read_cpi_data(raw_data[3], dt)
        csi = compute_csi(baskets, cpi)

        data.append(Month(dt, covid_cases, unemployment_rate, baskets, cpi, csi))

    if predict:
        complete_dataset(data)
    return data


def read_covid_data(data: list[list[str]], month: date) -> int:
    """Returns a tuple containing COVID case counts and the COVID transmission
    rate for a specified month.
    """
    cases = 0

    for row in data:
        row_year = int(row[3].split('-')[0])
        row_month = int(row[3].split('-')[1])
        dt = date(row_year, row_month, 1)

        # row[0] contains province ID, ID 1 is statistics for all of Canada
        if int(row[0]) == 1 and month == dt:
            cases = cases + float(row[15])

    return cases


def read_unemployment_data(data: list[list[str]], month: date) -> float:
    """Returns the float unemployment rate for a specified month.
    """
    start_date = date(1960, 1, 1)
    row = relativedelta(month, start_date).months + (relativedelta(month, start_date).years * 12)
    return float(data[row][1])


def read_baskets_data(data: list[list[str]], month: date) -> dict:
    """Returns a dictionary containing the weighted baskets for specific commodities
    for a specified month.
    """
    basket_coords = [1.1, 1.2, 1.21, 1.35, 1.67, 1.83, 1.92, 1.117]
    baskets = {}

    idx = 0
    current = ''
    for row in data:
        dt = date(int(row[0].split('-')[0]), int(row[0].split('-')[1]), 1)
        if month == dt:
            if idx < len(basket_coords) and float(row[9]) == basket_coords[idx]:
                idx = idx + 1
                current = ''.join([letter for letter in row[3]
                                   if letter.isalpha() or letter == ' '])
                baskets[current] = Basket(row[3], float(row[10]), {})
            else:
                baskets[current].categories[row[3]] = float(row[10])

    return baskets


def read_cpi_data(data: list[list[str]], month: date) -> dict:
    """Returns a dictionary of the relative cost of specific commodities for a specified
    month.
    """
    cpi = {}

    for row in data:
        dt = date(int(row[0].split('-')[0]), int(row[0].split('-')[1]), 1)
        if row[1] == 'Canada' and dt == month:
            cpi[''.join([letter for letter in row[3] if letter.isalpha() or letter == ' '])]\
                = float(row[10])

    return cpi


def compute_csi(baskets: dict, cpi: dict) -> dict:
    """Returns a dictionary containing the consumer spending index, which is calculated per
    each commodity using basket data and the consumer price index.
    """
    csi = {}

    for basket in baskets:
        if basket == 'Allitems':
            continue
        csi[basket] = (baskets[basket].weight / 100.0) * cpi[basket]

    csi['Total'] = sum(csi.values())
    return csi


def predict_next_wave(data: list[Month], next_cases: list[int], category: str = 'Total') -> None:
    """Mutates given data by predicting another wave of cases
    and adds new months to the list.

    This function is not used in the final application due to
    the unreliability of the model, and only remains as a
    further demonstration of the capabilities of the Predictor class.
    A full explanation on the flaws of the predictive model can be
    found in the discussion section of the report.

    Sample usage (based on the case counts from Oct. 2020 to Feb. 2021/'the second wave'):
    >>> dt = load_data(date(2020, 3, 1), date(2021, 1, 1))
    >>> predict_next_wave(dt, [76686, 142695, 203288, 198426, 87841])
    """
    cases = [m.covid_cases for m in data]
    csi = [m.csi[category] for m in data]
    predictor = Predictor(cases, csi)
    start_date = data[-1].date

    for count in next_cases:
        start_date = start_date + relativedelta(months=1)
        pred_csi = predictor.make_prediction(count)
        month = Month(start_date, count, 0.0, {}, {}, {category: pred_csi})
        data.append(month)


def complete_dataset(data: list[Month]) -> None:
    """Fills in missing CSI values where data for computation is not
    available using a predictive model based on existing data."""
    cases = []
    csi = []

    for month in data:
        if month.csi['Total'] > 0.0:
            cases.append(month.covid_cases)
            csi.append(month.csi)

    for category in csi[0]:
        csi_for_category = [c[category] for c in csi]
        predictor = Predictor(cases, csi_for_category)
        for month in data:
            if category not in month.csi:
                month.csi[category] = predictor.make_prediction(month.covid_cases)
            elif month.csi[category] <= 0.0:
                month.csi['Predicted Total'] = predictor.make_prediction(month.covid_cases)

    for month in data:
        if month.csi['Total'] <= 0.0:
            month.csi['Total'] = sum(month.csi.values()) - month.csi['Predicted Total']


if __name__ == '__main__':
    import python_ta
    import python_ta.contracts

    python_ta.contracts.check_all_contracts()
    python_ta.check_all(config={
        'extra-imports': ['csv', 'datetime', 'dateutil.relativedelta', 'prediction'],
        'allowed-io': ['load_csv'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import doctest

    doctest.testmod()
