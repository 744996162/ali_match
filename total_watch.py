##coding=utf-8
__author__ = 'Administrator'
from collections import defaultdict
from pandas import DataFrame
from pandas import Timestamp
from pandas import Series


"""
mfd_bank_shibor.csv 利率数据
mfd_day_share_interest.csv
user_profile_table.csv  用户信息表


user_balance_table.csv 用户申购赎回数据

user_id
report_date

tBalance 今日余额
yBalance 昨日余额

total_purchase_amt 今日总购买量=直接购买+收益
direct_purchase_amt 今日直接购买量
purchase_bal_amt 今日支付宝余额购买量
purchase_bank_amt 今日银行卡购买量


total_redeem_amt 今日总赎回量=消费+转出
consume_amt  今日消费总量
transfer_amt 今日转出总量
tftobal_amt 今日转出到支付宝余额总量
tftocard_amt 今日转出到银行卡总量
share_amt 今日收益

category1
category2
category3
category4
"""

def get_dataframe():
    path = "data/user_balance_table.data"
    #总余额
    tBalance_all = dict()
    #总申购量
    total_purchase = dict()
    #总赎回量
    total_redeem = dict()

    for line in open(path):
        (user_id, report_date, tBalance, yBalance, total_purchase_amt, direct_purchase_amt,
         purchase_bal_amt, purchase_bank_amt, total_redeem_amt, consume_amt, transfer_amt,
         tftobal_amt, tftocard_amt, share_amt, category1, category2, category3, category4) = line.strip().split(",")

        tBalance_all.setdefault(report_date, 0)
        tBalance_all[report_date] += int(tBalance)

        total_purchase.setdefault(report_date, 0)
        total_purchase[report_date] += int(total_purchase_amt)

        total_redeem.setdefault(report_date, 0)
        total_redeem[report_date] += int(total_redeem_amt)


    key_list = []
    tBalance_all_list = []
    total_purchase_list = []
    total_redeem_list = []
    total_diff_list = []

    for key in sorted(tBalance_all):
        # print(key, tBalance_all[key], total_purchase[key], total_redeem[key], total_purchase[key]-total_redeem[key])
        key_list.append(key)
        tBalance_all_list.append(tBalance_all[key])
        total_purchase_list.append(total_purchase[key])
        total_redeem_list.append(total_redeem[key])
        total_diff_list.append(total_purchase[key]-total_redeem[key])
        # print(key)

    df = DataFrame({"date": Series(Timestamp(key) for key in key_list),
                    "tBalance_all": Series(value for value in tBalance_all_list),
                   "total_purchase": Series(value for value in total_purchase_list),
                   "total_redeem": Series(value for value in total_redeem_list),
                   "total_diff": Series(value for value in total_diff_list)})

                   # "total_purchase": Series(total_purchase)
        # }, index= Series(Timestamp(key) for key in key_list))
        # print(user_id, report_date)

    df2 = DataFrame({

                    "tBalance_all": Series(value for value in tBalance_all_list),
                   "total_purchase": Series(value for value in total_purchase_list),
                   "total_redeem": Series(value for value in total_redeem_list),
                   "total_diff": Series(value for value in total_diff_list)})



    return df




if __name__ == "__main__":
    df = get_dataframe()
    print(df)
    # print(df["date"],df["total_purchase"],df["total_redeem"])