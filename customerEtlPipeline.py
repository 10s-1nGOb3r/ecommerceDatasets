import pandas as pd
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir,"input","ecommerce_sales_customer_analytics_150k.csv")
file_path2 = os.path.join(script_dir,"input","customer_master.csv")
file_path3 = os.path.join(script_dir,"input","order_items.csv")
file_path4 = os.path.join(script_dir,"input","product_catalog.csv")
file_path5 = os.path.join(script_dir,"input","currencyDb.csv")
save_at = os.path.join(script_dir,"output","ecommerceSalesCustomerCleanedTables.csv")
save_at2 = os.path.join(script_dir,"output","customerMasterCleanedTables.csv")
save_at3 = os.path.join(script_dir,"output","orderItemsCleanedTables.csv")
save_at4 = os.path.join(script_dir,"output","productCatalogCleanedTables.csv")
save_at5 = os.path.join(script_dir,"output","aggregationCustomerByCountry.csv")
save_at6 = os.path.join(script_dir,"output","aggregationCustomerByState.csv")
save_at7 = os.path.join(script_dir,"output","aggregationCustomerByCustomerSegment.csv")
save_at8 = os.path.join(script_dir,"output","aggregationCustomerByAgeGroup.csv")
save_at9 = os.path.join(script_dir,"output","aggregationSalesChannelByGender.csv")
save_at10 = os.path.join(script_dir,"output","aggregationProfitsAndSalesActivityPerCustomer.csv")
save_at11 = os.path.join(script_dir,"output","aggregationProfitsAndSalesPerCustomerSegment.csv")
save_at12 = os.path.join(script_dir,"output","aggregationProfitsAndSalesPerCustomerCountry.csv")
save_at13 = os.path.join(script_dir,"output","aggregationProfitsAndSalesPerCountryRegion.csv")

df = pd.read_csv(file_path,sep=",")
df2 = pd.read_csv(file_path2,sep=",")
df3 = pd.read_csv(file_path3,sep=",")
df4 = pd.read_csv(file_path4,sep=",")
df5 = pd.read_csv(file_path5,sep=";")

collection = ["delivery_days","estimated_delivery_days",
              "customer_rating","gross_sales",
              "discount_amount","tax_amount",
              "shipping_cost","net_sales",
              "product_cost","profit",
              "profit_margin_percentage","customer_lifetime_value"]

for field in collection:
    df[field] = df[field].fillna(0)
    df[field] = df[field].round(2)

collection2 = ["discount_percentage","shipping_cost"]

df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", dayfirst=True ,errors="coerce")
df["month_date"] = df["order_date"].dt.month
df["year_date"] = df["order_date"].dt.year
collection4 = ["month_date","year_date"]
for field4 in collection4:
    df[field4] = df[field4].astype(str)
df["keysToDf5"] = df["month_date"] + "." + df["year_date"] + "." + df["currency"]
df["countryRegion"] = df["customer_country"] + " " + df["region"]

#Keep this in your mind!
#profit = net_sales - product_cost - shipping_cost

conditions2 = [df5["month"] == "January",
               df5["month"] == "February",
               df5["month"] == "March",
               df5["month"] == "April",
               df5["month"] == "May",
               df5["month"] == "June",
               df5["month"] == "July",
               df5["month"] == "August",
               df5["month"] == "September",
               df5["month"] == "October",
               df5["month"] == "November",
               df5["month"] == "December"
]
choices2 = ["1","2","3","4","5","6"
            ,"7","8","9","10","11","12"]
df5["monthNumber"] = np.select(conditions2,choices2,default="0")
df5["year"] = df5["year"].astype(str)
df5["keysToDf"] = df5["monthNumber"] + "." + df5["year"] + "." + df5["currency"]

colsToKeep2 = ["keysToDf","toUSDExchange"]
df5Unique = df5[colsToKeep2].drop_duplicates(subset=["keysToDf"])
df = pd.merge(df,df5Unique,left_on="keysToDf5",right_on="keysToDf", how="left")
df["keysToDf"] = df["keysToDf"].fillna("0")
conditions3 = [(df["keysToDf"] == "0") & (df["payment_status"] == "Paid"),
               (df["keysToDf"] != "0") & (df["payment_status"] == "Paid"),
               (df["keysToDf"] == "0") & (df["payment_status"] != "Paid"),
               (df["keysToDf"] != "0") & (df["payment_status"] != "Paid")
]
choices3 = [1,df["toUSDExchange"],0,0]
df["toUSDExchange"] = np.select(conditions3,choices3,default=0)
df["profitInUsd"] = np.where((df["toUSDExchange"] > 0) & (df["profit"] > 0),(df["profit"] * df["toUSDExchange"]).round(2),0)
df["salesInUsd"] = np.where(df["toUSDExchange"] > 0,(df["gross_sales"] * df["toUSDExchange"]).round(2),0)
df["profit_margin_percentageFiltered"] = np.where(df["toUSDExchange"] > 0,(df["profit_margin_percentage"]).round(2),0)
collection9 = ["profitInUsd","salesInUsd"]
for field9 in collection9:
    df[field9] = df[field9].round(0).astype(int)

conditions = [(df2["customer_age"] >= 18) & (df2["customer_age"] <= 24),
              (df2["customer_age"] >= 25) & (df2["customer_age"] <= 34),
              (df2["customer_age"] >= 35) & (df2["customer_age"] <= 44),
              (df2["customer_age"] >= 45) & (df2["customer_age"] <= 54),
              (df2["customer_age"] >= 55) & (df2["customer_age"] <= 64),
              (df2["customer_age"] >= 65)]
choices = ["18-24","25-34",
           "35-44","45-54",
           "55-64",">65"]
df2["ageGroup"] = np.select(conditions,choices,default="0")

colsToKeep = ["customer_id", "ageGroup"]
df2Unique = df2[colsToKeep].drop_duplicates(subset=["customer_id"])
df = pd.merge(df,df2Unique,left_on="customer_id",right_on="customer_id", how="left")
df = df.dropna(subset=["customer_id"])

totalSales = len(df)

customerPerCountry = df2.groupby(["customer_country"]).agg(
    totalCustomerPerCountry = ("customer_country", "count")
).reset_index()
totalCustomer = len(df2)
customerPerCountry["perc"] = 100 * (customerPerCountry["totalCustomerPerCountry"] / totalCustomer)
customerPerCountry["perc"] = customerPerCountry["perc"].round(2)

customerPerState = df2.groupby(["customer_state"]).agg(
    totalCustomerPerState = ("customer_state", "count")
).reset_index()
customerPerState["perc"] = 100 * (customerPerState["totalCustomerPerState"] / totalCustomer)
customerPerState["perc"] = customerPerState["perc"].round(2)

customerPerCustomerSegment = df2.groupby(["customer_segment"]).agg(
    totalCustomerPerState = ("customer_segment", "count")
).reset_index()
customerPerCustomerSegment["perc"] = 100 * (customerPerCustomerSegment["totalCustomerPerState"] / totalCustomer)
customerPerCustomerSegment["perc"] = customerPerCustomerSegment["perc"].round(2)

customerPerAgeGroup = df2.groupby(["ageGroup"]).agg(
    totalCustomerPerAgeGroup = ("ageGroup", "count")
).reset_index()
customerPerAgeGroup["perc"] = 100 * (customerPerAgeGroup["totalCustomerPerAgeGroup"] / totalCustomer)
customerPerAgeGroup["perc"] = customerPerAgeGroup["perc"].round(2)

salesChannelByGender = df.groupby(["gender"]).agg(
    marketPlaceChannel = ("sales_channel", lambda x: (x == "Marketplace").sum()),
    mobileAppChannel = ("sales_channel", lambda x: (x == "Mobile App").sum()),
    socialMediaChannel = ("sales_channel", lambda x: (x == "Social Media").sum()),
    websiteChannel = ("sales_channel", lambda x: (x == "Website").sum())
).reset_index()
salesChannelByGender["marketPlaceChannelPerc"] = 100 * (salesChannelByGender["marketPlaceChannel"] / totalSales)
salesChannelByGender["mobileAppChannelPerc"] = 100 * (salesChannelByGender["mobileAppChannel"] / totalSales)
salesChannelByGender["socialMediaChannelPerc"] = 100 * (salesChannelByGender["socialMediaChannel"] / totalSales)
salesChannelByGender["websiteChannelPerc"] = 100 * (salesChannelByGender["websiteChannel"] / totalSales)
collection3 = ["marketPlaceChannelPerc",
               "mobileAppChannelPerc",
               "socialMediaChannelPerc",
               "websiteChannelPerc"]
for field3 in collection3:
    salesChannelByGender[field3] = salesChannelByGender[field3].round(2)

salesByCustomerId = df.groupby(["year_date","month_date","customer_id"]).agg(
    totalPurchasingActivityPerCustomer = ("customer_id","count"),
    totalProfitsMakingPerCustomer = ("profitInUsd","sum"),
    totalSalesPerCustomer = ("salesInUsd","sum"),
    averageMarginProfitsPerCustomer = ("profit_margin_percentageFiltered","mean")
).reset_index()

salesAndProfitsByCustomerSegment = df.groupby(["year_date","month_date","customer_segment"]).agg(
    totalPurchasingActivityPerCustomerSegment = ("customer_id","count"),
    totalProfitsMakingPerCustomerSegment = ("profitInUsd","sum"),
    totalSalesPerCustomerSegment = ("salesInUsd","sum"),
    averageMarginProfitsPerCustomerSegment = ("profit_margin_percentageFiltered","mean")
).reset_index()

salesAndProfitsByCustomerCountry = df.groupby(["year_date","month_date","customer_country"]).agg(
    totalPurchasingActivityPerCustomerCountry = ("customer_id","count"),
    totalProfitsMakingPerCustomerCountry = ("profitInUsd","sum"),
    totalSalesPerCustomerCountry = ("salesInUsd","sum"),
    averageMarginProfitsPerCustomerCountry = ("profit_margin_percentageFiltered","mean")
).reset_index()

salesAndProfitsByCountryRegion = df.groupby(["year_date","month_date","countryRegion"]).agg(
    totalPurchasingActivityPerCountryRegion = ("customer_id","count"),
    totalProfitsMakingPerCountryRegion = ("profitInUsd","sum"),
    totalSalesPerCountryRegion = ("salesInUsd","sum"),
    averageMarginProfitsPerCountryRegion = ("profit_margin_percentageFiltered","mean")
).reset_index()

collection5 = [salesByCustomerId,
               salesAndProfitsByCustomerSegment,
               salesAndProfitsByCustomerCountry,
               salesAndProfitsByCountryRegion]
collection6 = ["averageMarginProfitsPerCustomer",
               "averageMarginProfitsPerCustomerSegment",
               "averageMarginProfitsPerCustomerCountry",
               "averageMarginProfitsPerCountryRegion"]
for field5 in collection5:
    for field6 in collection6:
        if field6 in field5.columns:
            field5[field6] = field5[field6].round(2)

collection7 = [salesByCustomerId,
               salesAndProfitsByCustomerSegment,
               salesAndProfitsByCustomerCountry,
               salesAndProfitsByCountryRegion]
collection8 = {"averageMarginProfitsPerCustomer": "averageMarginProfitsPerCustomerForPbi",
               "averageMarginProfitsPerCustomerSegment": "averageMarginProfitsPerCustomerSegmentForPbi",
               "averageMarginProfitsPerCustomerCountry": "averageMarginProfitsPerCustomerCountryForPbi",
               "averageMarginProfitsPerCountryRegion": "averageMarginProfitsPerCountryRegionForPbi"}
for field7 in collection7:
    for field8, field9 in collection8.items():
        if field8 in field7.columns:
            field7[field9] = field7[field8].round(2).astype(str).str.replace(".", ",", regex=False)

df.info()

df.to_csv(save_at,sep=";",index=False)
df2.to_csv(save_at2,sep=";",index=False)
df3.to_csv(save_at3,sep=";",index=False)
df4.to_csv(save_at4,sep=";",index=False)
df5.to_csv(save_at4,sep=";",index=False)
customerPerCountry.to_csv(save_at5,sep=";",index=False)
customerPerState.to_csv(save_at6,sep=";",index=False)
customerPerCustomerSegment.to_csv(save_at7,sep=";",index=False)
customerPerAgeGroup.to_csv(save_at8,sep=";",index=False)
salesChannelByGender.to_csv(save_at9,sep=";",index=False)
salesByCustomerId.to_csv(save_at10,sep=";",index=False)
salesAndProfitsByCustomerSegment.to_csv(save_at11,sep=";",index=False)
salesAndProfitsByCustomerCountry.to_csv(save_at12,sep=";",index=False)
salesAndProfitsByCountryRegion.to_csv(save_at13,sep=";",index=False)
