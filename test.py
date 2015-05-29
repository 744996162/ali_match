__author__ = 'Administrator'
from sklearn import svm
from tools import *
import math



class DataContainer():
    def __init__(self, u_list, pr_map, up_map, td_map, bd_map):
        self.user_day_item_list = u_list
        self.purchase_redeem_map = pr_map
        self.user_profile_map = up_map
        self.taobao_day_map = td_map
        self.bank_day_map = bd_map

class Predictor():
    def __init__(self, data_container):
        self.purchase_rate = 0.45
        self.redeem_rate = 0.55
        self.max_predict_day_num = 31
        self.data = data_container
        self.train_valid_date = "" # train_valid_date - 1 is the last valid date in training process

    def math_log(self, x):
        return math.log10(1.0 + x)

    def math_exp(self, x):
        return (10.0 ** x) - 1.0

    def train_purchase(self):
        pass

    def train_redeem(self):
        pass

    def train(self, tv_date):
        self.train_valid_date = tv_date
        self.train_purchase()
        self.train_redeem()

    def predict_purchase(self, begin_date, end_date):
        pass

    def predict_redeem(self, begin_date, end_date):
        pass

    def predict(self, begin_date, end_date):
        predict_map = {}
        purchase_predict_map = self.data.predict_purchase(begin_date, end_date)
        redeem_predict_map = self.data.predict_purchase(begin_date, end_date)
        predict_date = end_date
        while predict_date != begin_date:
            predict_date = add_day(predict_date, -1)
            predict_map[predict_date] = [0, 0]
            predict_map[predict_date][0] = purchase_predict_map[predict_date]
            predict_map[predict_date][1] = redeem_predict_map[predict_date]
        return predict_map

    def test_performance(self, begin_date, end_date):
        predict_results = self.predict(begin_date, end_date)
        p_score_list = []
        r_score_list = []
        s_list = []
        date_str = begin_date
        while date_str != end_date:
            p_value = predict_results[date_str][0]
            r_value = predict_results[date_str][1]
            p_real = self.data.purchase_redeem_map[date_str][0]
            r_real = self.data.purchase_redeem_map[date_str][1]
            p_score_list.append([date_str, p_value, p_real, self.calculate_purchase_score(p_value, p_real)])
            r_score_list.append([date_str, r_value, r_real, self.calculate_purchase_score(r_value, r_real)])
            s_list.append([date_str, self.calculate_score(p_value, p_real, r_value, r_real)])
            date_str = add_day(date_str)
        ret_str = ""
        ret_str += result_arr("Total Score: ", s_list) + "\n"
        ret_str += result_arr("Purchase Score: ", p_score_list) + "\n"
        ret_str += result_arr("Redeem Score: ", r_score_list) + "\n"
        print ret_str
        return ret_str

    def calculate_purchase_score(self, predict_value, real_value):
        purchase = 1.0 * abs(predict_value - real_value) / real_value
        score = max(0.0, (0.3 - purchase)) / 0.3 * 10
        return score

    def calculate_redeem_score(self, predict_value, real_value):
        redeem = 1.0 * abs(predict_value - real_value) / real_value
        score = max(0.0, (0.3 - redeem)) / 0.3 * 10
        return score

    def calculate_score(self, p_predict, p_real, r_predict, r_real):
        return self.purchase_rate * self.calculate_purchase_score(p_predict, p_real) + self.redeem_rate * self.calculate_redeem_score(r_predict, r_real)

class NaivePredictor(Predictor):
    def predict(self, begin_date, end_date):
        predict_map = {}
        predict_date = end_date
        source_date = begin_date
        while predict_date != begin_date:
            predict_date = add_day(predict_date, -1)
            source_date = add_day(source_date, -1)
            predict_map[predict_date] = [0, 0]
            predict_map[predict_date][0] = self.data.purchase_redeem_map[source_date][0]
            predict_map[predict_date][1] = self.data.purchase_redeem_map[source_date][1]
        return predict_map

class SimpleRegressionPredictor(Predictor):
    def __init__(self, data_container, mtc_num = 120, fbt_num = 15):
        Predictor.__init__(self, data_container)
        self.purchase_model = svm.SVR()
        self.redeem_model = svm.SVR()
        self.feature_back_trace_day_num = fbt_num
        self.max_train_case_num = mtc_num

    def build_feature(self, target_date_str):
        feature_begin_date = add_day(target_date_str, -1 * (self.feature_back_trace_day_num))
        if not self.data.purchase_redeem_map.has_key(feature_begin_date):
            return None
        feature_list = []
        feature_date = feature_begin_date
        i = 0
        while i < self.feature_back_trace_day_num:
            feature_list.append(self.data.purchase_redeem_map[feature_date][0])#purchase value
            feature_list.append(self.data.purchase_redeem_map[feature_date][1])#redeem value
            #for k in range(1, 3):
            #    feature_list.append(self.data.taobao_day_map[feature_date][k])
            #for k in range(1, 9):
            #    feature_list.append(self.data.bank_day_map[feature_date][k])
            feature_date = add_day(feature_date)
            i += 1
        #print "feature: " + str(feature_list)
        return feature_list

    def train_target_index(self, index, model):
        train_x_map = {}
        train_x_list = []
        train_y = []
        #init data
        date_str = self.train_valid_date
        train_case_count = 0
        while True:
            date_str = add_day(date_str, -1)
            feature_list = self.build_feature(date_str)
            if not feature_list:
                break
            train_y.append(self.data.purchase_redeem_map[date_str][index])
            train_x_map[date_str] = feature_list
            train_case_count += 1
            if train_case_count >= self.max_train_case_num:
                break
        sorted_key_list = sorted(train_x_map.keys(), key= lambda x: x, reverse=False)
        for key in sorted_key_list:
            train_x_list.append(train_x_map[key])
        model.fit(train_x_list, train_y)

    def train_purchase(self):
        self.train_target_index(0, self.purchase_model)

    def train_redeem(self):
        self.train_target_index(1, self.redeem_model)

    def predict(self, begin_date, end_date):
        predict_map = {}
        predict_date = begin_date
        feature_list = self.build_feature(begin_date)
        while predict_date != end_date:
            predict_map[predict_date] = [0, 0]
            predict_map[predict_date][0] = int(self.purchase_model.predict(feature_list))
            predict_map[predict_date][1] = int(self.redeem_model.predict(feature_list))
            #update feature for next date
            feature_list.pop(1)
            feature_list.pop(0)
            feature_list.append(predict_map[predict_date][0])
            feature_list.append(predict_map[predict_date][1])
            predict_date = add_day(predict_date)
        return predict_map


def test_SimpleRegressionPredictor():

    data_dir = "data"
    data_begin_date = "20130701"
    data_end_date = "20140831"


    user_day_item_list = load_items(data_dir + "/user_balance_table.csv", "UserDayItem")
    # user_day_item_dict = load_map_items(user_day_item_list)

    user_profile_map = load_map_items(load_items(data_dir + "/user_profile_table.csv", "UserProfileItem"))
    alipay_share_map = load_map_items(load_items(data_dir + "/mfd_day_share_interest.csv", "AlipayShareItem"))
    bank_day_map = load_map_items(load_items(data_dir + "/mfd_bank_shibor.csv", "BankDayItem"))
    purchase_map = build_purchase_redeem_map(data_begin_date, "20140901", user_day_item_list)



    data_container = DataContainer(user_day_item_list, purchase_map, user_profile_map,alipay_share_map, bank_day_map)

    o_object = SimpleRegressionPredictor(data_container)
    result_dict = o_object.predict("20140901", "20140930")
    for k,v in result_dict.items():
        print(k,v)

    pass


if __name__ == "__main__":
    print("hello ")
    test_SimpleRegressionPredictor()
    pass