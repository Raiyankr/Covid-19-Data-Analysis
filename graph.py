"""Evaluating the impact of COVID-19 on Canadians’ spending habits: graphing module

This module is responsible for loading, filtering and displaying data using plotly.

Copyright and Usage Information
===============================
This file is Copyright (c) 2021 Ajinkya Bhosale.
"""
from datetime import date
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from backend import load_data

# Load in all the data available(including the predicted data from Mar 2020 to Oct 2021)
main_data = load_data(date(2020, 3, 1), date(2021, 10, 1), True)
main_data = pd.DataFrame(main_data)  # turned the data into DataFrame object


def get_filtered_data(start_date: date, end_date: date) -> pd.DataFrame:
    """Returns a copy of the data for a selected date range

    The 'main-data' is fetched once everytime the program starts. If a user would like to
    shorten/change the date range to be displayed in the graph, a 'copy' is made out of the
    main_data to avoid computing it over and over.

    Sample usage:
    To filter data from March 2020 to February 2021:
    >>> start_dt = date(2020, 3, 1)
    >>> end_dt = date(2021, 2, 1)
    >>> filtered_data = get_filtered_data(start_dt, end_dt)
    """
    filtered_data = main_data.loc[(main_data['date'] >= start_date)
                                  & (main_data['date'] <= end_date)]

    return filtered_data


def normalize_data(filtered_data: pd.DataFrame, usr_choice: list) -> object:
    """Return the attribute values that are normalized form the provided filtered_data and
    a list containing attribute names to normalize.
    The data is normalized on a scale of 0-10.

    The returned data is a nested list containing list of normalized values for each attribute.
    The list preserves odrer: the index of in the input list corrosponds to the index of the
    nested list from the output

    Sample Usage:
    To normalize values to Covid Cases and CPI.
    >>> start_dt = date(2020, 3, 1)
    >>> end_dt = date(2021, 2, 1)
    >>> filtered_data = get_filtered_data(start_dt, end_dt)
    >>> normalize_data(filtered_data, ['covid_cases', 'cpi'])
    """
    scaling = MinMaxScaler((0, 10))
    list_so_far = []
    for choice in usr_choice:
        if choice == 'covid_cases':
            arr = scaling.fit_transform(filtered_data['covid_cases'].values.reshape(-1, 1))
            temp = np.reshape(arr, arr.__len__())
            list_so_far.append(temp.tolist())
        elif choice == 'unemployment_rate':
            arr = scaling.fit_transform(filtered_data['unemployment_rate'].values.reshape(-1, 1))
            temp = np.reshape(arr, arr.__len__())
            list_so_far.append(temp.tolist())
        elif choice == 'csi':
            arr = scaling.fit_transform(filtered_data.csi.str['Total'].values.reshape(-1, 1))
            temp = np.reshape(arr, arr.__len__())
            list_so_far.append(temp.tolist())
        elif choice == 'cpi':
            arr = scaling.fit_transform(filtered_data.cpi.str['Allitems'].values.reshape(-1, 1))
            temp = np.reshape(arr, arr.__len__())
            list_so_far.append(temp.tolist())

    return list_so_far


def line_graph(filtered_data: pd.DataFrame, usr_choice: list[str]) -> None:
    """Normal Line Graph plotting function that takes user's choice of data to be displayed.

    Sample Use:
    # NOTE: some lines are commented instead of written as doctests as otherwise
    doctest.testmod() will cause browser windows to open with graphs
    # To display the line graph with covid cases and unemployenment rate with respect to time
    >>> start_dt = date(2020, 3, 1)
    >>> end_dt = date(2021, 2, 1)
    >>> filtered_data = get_filtered_data(start_dt, end_dt) # apply users date filters on the data
    # line_graph(filtered_data, ['covid_cases', 'unemployment_rate'])

    # To display the line graph with all the attributes(except baskets) **
    # line_graph(filtered_data, ['covid_cases', 'unemployment_rate', 'cpi', 'csi'])

    """
    fig = px.line(filtered_data, x="date", y=normalize_data(filtered_data, usr_choice),
                  labels={"variable": "Category", "date": "Time"},
                  title="Covid-Related Graphs")

    for i in range(len(usr_choice)):
        fig.data[i].name = usr_choice[i]
        fig.data[i].hovertemplate = 'Category = ' \
                                    + usr_choice[i] + '<br>date=%{x}<br>value=%{y}<extra></extra>'

    fig.show()


def animated_graph(filtered_data: pd.DataFrame, usr_choice: list[str]) -> None:
    """Animated line graph plotting function takes user's choice of data to be displayed.

       Sample Usage:
       # NOTE: some lines are commented instead of written as doctests as otherwise
        doctest.testmod() will cause browser windows to open with graphs
       # To display the line graph with covid cases and unemployenment rate with respect to time
       >>> start_dt = date(2020, 3, 1)
       >>> end_dt = date(2021, 2, 1)
       >>> filtered_data = get_filtered_data(start_dt, end_dt) # apply users date filters on the data
       # animated_graph(filtered_data, ['covid_cases', 'unemployment_rate'])

       # To display the line graph with all the attributes(except baskets) **
       # animated_graph(filtered_data, ['covid_cases', 'unemployment_rate', 'cpi', 'csi'])
    """

    fig = px.scatter(filtered_data, x="date", y=normalize_data(filtered_data, usr_choice),
                     animation_frame=[da.__str__() for da in filtered_data.date],
                     range_x=(date(2020, 3, 1), date(2021, 10, 1)),
                     range_y=(-0.5, 12),
                     labels={"variable": "Category", "date": "Time"},
                     title="Animated Covid-Related Graphs")

    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1200
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 1200
    for i in range(len(usr_choice)):
        fig.data[i].name = usr_choice[i]
        fig.data[i]['marker'].update(size=14)
        fig.data[i].hovertemplate = 'Category = ' \
                                    + usr_choice[i] + '<br>date=%{x}<br>value=%{y}<extra></extra>'

    pio.show(fig)


def csi_bar_chart(filtered_data: pd.DataFrame) -> None:
    """Bar Graph plotting function that takes user's choice of date range to be displayed.

    Sample Use:
       # To display the bar graph of subcatrgories of CSI.
       # NOTE: some lines are commented instead of written as doctests as otherwise
        doctest.testmod() will cause browser windows to open with graphs
       >>> start_dt = date(2020, 3, 1)
       >>> end_dt = date(2021, 2, 1)
       >>> filtered_data = get_filtered_data(start_dt, end_dt) # apply users date filters on the data
       # csi_bar_chart(filtered_data)
    """

    categories = ['Shelter', 'Food', 'Transportation',
                  'Household operations furnishings and equipment',
                  'Recreation education and reading', 'Health and personal care',
                  'Alcoholic beverages tobacco products and recreational cannabis']

    cat_values = [filtered_data.csi.str[cat].values.tolist() for cat in categories]

    fig = px.bar(filtered_data, x='date', y=cat_values,
                 labels={"variable": "Category", "date": "Time",
                         "value": "Percentage spending compared to (2002)"},
                 title="Change in CSI Categories in Relation to Time")

    for i in range(len(categories)):
        fig.data[i].name = categories[i]
        fig.data[i].hovertemplate = 'Category = ' \
                                    + categories[i] + '<br>date=%{x}<br>value=%{y}<extra></extra>'

    fig.show()


if __name__ == '__main__':
    import python_ta
    import python_ta.contracts

    python_ta.contracts.check_all_contracts()
    python_ta.check_all(config={
        'extra-imports': ['datetime', 'pandas', 'plotly', 'plotly.io', 'plotly.express', 'numpy',
                          'sklearn.preprocessing', 'backend'],
        'allowed-io': ['load_csv'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import doctest

    doctest.testmod()
