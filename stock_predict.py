import tushare as ts
import pandas as pd


class StockPredict:
    def __init__(self):
        pro = ts.pro_api()

        self.daily_data_df = pro.daily(ts_code='002603.SZ', start_date='20220101', end_date='20221201')

    def is_red(self, data, i, n):
        if i > len(data) - n:
            return False
        else:
            res = True
            for j in range(i, i + n):
                res = res and data.close[j] > data.open[j]
                if not res: return False
            return res

    def is_open_in_last_entity(self, data, i, n):
        if i > len(data) - n - 1:
            return False
        else:
            res = True
            for j in range(i, i + n):
                res = res and data.open[j] > data.open[j + 1]
                if not res: return False
            return res

    def is_close_near_high(self, data, i, n, p=0.01):
        if i > len(data) - n:
            return False
        else:
            res = True
            for j in range(i, i + n):
                if (data.high[j] <= 0): return False
                res = res and (data.high[j] - data.close[j]) / data.high[j] < p
            return res

    def is_entity_equal(self, data, i, n, p=0.8):
        if i > len(data) - n:
            return False
        else:
            Max = 0
            Min = 10000
            Sum = 0

            for j in range(i, i + n):
                e = abs(data['close'][j] - data['open'][j])
                if e > Max: Max = e
                if e < Min: Min = e
                Sum = Sum + e

            if Sum > 0 and n > 0 and (Max - Min) / (Sum / n) < p:
                return True
            else:
                return False

    def is_red_3_soldier(self, data, i, p1=3, p2=0.01, p3=0.8):
        if i > len(data) - p1:
            return False
        else:
            res1 = self.is_red(data, i, p1) and self.is_open_in_last_entity(data, i, p1 - 1)
            res2 = self.is_close_near_high(data, i, p1, p2) and self.is_entity_equal(data, i, p1, p3)
            return res1 and res2

    def moving_average_five(self, earning_rates):
        res = [0 for _ in range(len(earning_rates))]
        for i in range(0, 5):
            res[i] = earning_rates[i]
        for i in range(5, len(earning_rates)):
            res[i] = sum(earning_rates[i - 5:i]) / 5
        return res


if __name__ == '__main__':
    stock_predictor = StockPredict()
    data = stock_predictor.daily_data_df
    earning_rates = data['pct_chg'].tolist()
    predict_earing_rates = stock_predictor.moving_average_five(earning_rates)
    red3s = pd.Series(0.0, index=range(len(data)))
    for i in range(len(data)):
        if stock_predictor.is_red_3_soldier(data, i, 3, 0.01, 0.8):
            red3s[i] = 3
        else:
            red3s[i] = predict_earing_rates[i]
    stock_predictor.daily_data_df['预测收益率'] = red3s
    stock_predictor.daily_data_df['预测收益率与实际收益率差值'] = stock_predictor.daily_data_df['预测收益率'] - \
                                                     stock_predictor.daily_data_df['pct_chg']
    # stock_predictor.daily_data_df.to_excel(r'以岭药业股价.xlsx', index=False)
    D_value = stock_predictor.daily_data_df['预测收益率与实际收益率差值'].tolist()
    avg_D_value = sum([abs(i) for i in D_value])/len(D_value)
    print('预测收益率与实际收益率差值的平均差值为:', avg_D_value)
    sum_xy = 0
    sum_x2 = 0
    sum_y2 = 0
    daily_rtn = pd.Series(0.0, index=range(244))
    for i in range(len(data)):
        sum_xy += red3s[i] * earning_rates[i]
        sum_x2 += red3s[i] * red3s[i]
        sum_y2 += earning_rates[i] * earning_rates[i]
    corr = sum_xy / pow(sum_x2 * sum_y2, 0.5)
    print('预测收益率与真实收益率的相关系数:', corr)

