import pandas as pd
import pymysql

from sqlalchemy import create_engine # type: ignore
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------- 1. 数据库连接配置----------------------
user = "root"
password = "060121"
host = "127.0.0.1"
port = 3306
db_name = "user_analysis"

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}')
conn = pymysql.connect(host=host,user=user,password=password,database=db_name,charset="utf8mb4")


# ---------------------- 2. 读取CSV数据集，写入MySQL----------------------
df = pd.read_csv("D:\用户行为数据\用户行为分析\用户行为分析.csv")
# 写入数据库
df.to_sql(name="user_behavior",con=engine,if_exists="replace",index=False)
print("数据成功导入MySQL")

# ---------------------- 3. SQL分析：核心业务指标查询 ----------------------
# 3.1 整体转化率：最终完成订单确认的用户占比
sql1 = """
SELECT 
    COUNT(*) AS total_user,
    SUM(CASE WHEN confirmation_page > 0 THEN 1 ELSE 0 END) AS pay_success_user,
    ROUND(SUM(CASE WHEN confirmation_page > 0 THEN 1 ELSE 0 END)/COUNT(*)*100,2) AS final_convert_rate
FROM user_behavior;
"""
df1 = pd.read_sql(sql1,conn)
print("====整体转化指标====")
print(df1)

#3.2 各流量渠道的转化率
sql2 = """
SELECT source,
COUNT(*) AS user_cnt,
ROUND(SUM(IF(confirmation_page>0,1,0))/COUNT(*)*100,2) convert_rate
FROM user_behavior
GROUP BY source
ORDER BY convert_rate DESC;
"""
df_source = pd.read_sql(sql2,conn)
print("\n====各渠道转化率====")
print(df_source)

#3.3 用户流失漏斗：首页→列表页→商品页→支付页→确认页
sql3 = """
SELECT
SUM(home_page>0) as home,
SUM(listing_page>0) as listing,
SUM(product_page>0) as product,
SUM(payment_page>0) as payment,
SUM(confirmation_page>0) as confirm
FROM user_behavior;
"""
df_funnel = pd.read_sql(sql3,conn)
print("\n====转化漏斗数据====")
print(df_funnel)

# ----------------------4. Python可视化：转化漏斗图、渠道转化率柱状图 ----------------------
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 漏斗图
funnel_data = df_funnel.iloc[0].values
funnel_name = ["首页","列表页","商品详情页","支付页","订单确认页"]
plt.figure(figsize=(10,5))
plt.bar(funnel_name,funnel_data,color="#4472C4")
plt.title("用户访问转化漏斗")
plt.ylabel("访问用户数")
plt.show()

# 渠道转化率柱状图
plt.figure(figsize=(10,5))
sns.barplot(data=df_source,x="source",y="convert_rate")
plt.title("不同流量渠道转化率对比")
plt.xlabel("流量来源渠道")
plt.ylabel("转化率(%)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

# ----------------------5. 用户画像：年龄&性别分布 ----------------------
sql4 = """
SELECT age,sex,COUNT(*) user_count
FROM user_behavior
GROUP BY age,sex
ORDER BY age;
"""
df_user = pd.read_sql(sql4,conn)
print("\n====用户年龄性别分布====")
print(df_user)

# =====用户年龄性别画像图=====
plt.figure(figsize=(10,5))
sns.barplot(data=df_user,x="age",y="user_count",hue="sex")
plt.title("用户年龄性别分布")
plt.xlabel("年龄")
plt.ylabel("用户数量")
plt.tight_layout()
plt.savefig("用户年龄性别分布.png",dpi=300,bbox_inches="tight")
plt.show()

# 关闭连接
conn.close()
print("\n完成！")
