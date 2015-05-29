__author__ = 'Administrator'
import numpy as np
import statsmodels.tsa.api
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.vector_ar.plotting import plot_var_forc
import pylab
import matplotlib.pyplot as plt
# from statsmodels.tsa.api import VAR
from statsmodels import datasets
import datetime
import pandas
from total_watch import get_dataframe
from pandas import Series
from pandas import DataFrame
import os

# data_dir = "data"
# user_profile_table_path = data_dir + "/user_profile_table.csv"
# user_balance_table_path = data_dir+"/user_balance_table.csv"
#
#
# df_user_profile = pandas.read_csv(user_profile_table_path)
# df_user_balance = pandas.read_csv(user_balance_table_path)

def vars_test():
    dt = get_dataframe()
    name_list = ["date", "tBalance_all", "total_purchase", "total_redeem", "total_diff"]
    # print(dt["total_purchase"])
    time = dt["date"]
    mdata = dt[["tBalance_all", "total_purchase", "total_redeem"]]
    mdata.index = pandas.DatetimeIndex(time)
    data = np.log(mdata).diff().dropna()
    model = VAR(data)
    results = model.fit(2)
    results.summary()

    results.plot()

    # print(results.summary())


    # print model.select_order(30)
    # print(mdata)

    # results = statsmodels.tsa.api.VAR(dt["total_purchase"], dt["total_redeem"])
    # print(results)
    # pass


def test2():
    mdata = statsmodels.datasets.macrodata.load_pandas().data
    dates = mdata[["year", "quarter"]].astype(int).astype(str)
    quarterly = dates["year"] + "Q" + dates["quarter"]

    mdata = mdata[["realgdp", "realcons", "realinv"]]
    mdata.index = pandas.DatetimeIndex(quarterly)
    data = np.log(mdata).diff().dropna()

    model = VAR(data)
    results = model.fit(2)
    results.summary()
    results = model.fit(maxlags=50, ic="aic")
    # print(results.summary())

    lag_order = results.k_ar
    print results.forecast(data.values[-lag_order:], 30)
    # print(results)
    # print model.select_order(15)

    # results.plot()
    # results.plot_acorr()

    pass




if __name__ == "__main__":
    vars_test()
    # test2()
    # test3()

    pass