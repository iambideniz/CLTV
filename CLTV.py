##########################################################
# CLTV = (Customer_Value / Churn_Rate) x Profit_margin.
##########################################################

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', 20)
pd.set_option('display.float_format', lambda x: '%.5f' % x)


df_=df_ = pd.read_excel("hafta 3/ödev/RFM/online_retail_II.xlsx",sheet_name="Year 2010-2011")

df=df_.copy()
df.head()

##################################################
# DATA PREPARATION
##################################################

df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[(df['Quantity'] > 0)]
df.isnull().sum()
df.dropna(inplace=True)
df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()


cltv_c = df.groupby('Customer ID').agg({'Invoice': lambda x: x.nunique(),
                                        'Quantity': lambda x: x.sum(),
                                        'TotalPrice': lambda x: x.sum()})

cltv_c.columns = ['total_transaction', 'total_unit', 'total_price']

cltv_c.head()

##################################################
# Average Order Value (average_order_value = total_price / total_transaction)
##################################################

cltv_c['avg_order_value'] = cltv_c['total_price'] / cltv_c['total_transaction']

##################################################
# Purchase Frequency (total_transaction / total_number_of_customers)
##################################################

cltv_c["purchase_frequency"] = cltv_c['total_transaction'] / cltv_c.shape[0]

##################################################
# Repeat Rate & Churn Rate (birden fazla alışveriş yapan müşteri sayısı / tüm müşteriler)
##################################################

repeat_rate = cltv_c[cltv_c.total_transaction > 1].shape[0] / cltv_c.shape[0]
churn_rate = 1 - repeat_rate

##################################################
# Profit Margin (profit_margin =  total_price * 0.10)
##################################################

cltv_c['profit_margin'] = cltv_c['total_price'] * 0.10

cltv_c.head()


##################################################
# Customer Value (customer_value = average_order_value * purchase_frequency)
##################################################

cltv_c['customer_value'] = cltv_c['avg_order_value'] * cltv_c["purchase_frequency"]

##################################################
# Customer Lifetime Value (CLTV = (customer_value / churn_rate) x profit_margin)
##################################################

cltv_c['cltv'] = (cltv_c['customer_value'] / churn_rate) * cltv_c['profit_margin']


# Standardization

scaler = MinMaxScaler(feature_range=(0, 1))
scaler.fit(cltv_c[["cltv"]])
cltv_c["scaled_cltv"] = scaler.transform(cltv_c[["cltv"]])


cltv_c.sort_values(by="scaled_cltv", ascending=False).head()


##################################################
# Segment
##################################################

cltv_c["segment"] = pd.qcut(cltv_c["scaled_cltv"], 4, labels=["D", "C", "B", "A"])

cltv_c[["total_transaction", "total_unit", "total_price", "cltv", "scaled_cltv"]].sort_values(by="scaled_cltv",
                                                                                              ascending=False).head()

# Segment Analysis

cltv_c.groupby("segment")[["total_transaction", "total_unit", "total_price", "cltv", "scaled_cltv"]].agg(
        {"count", "mean", "sum"})

