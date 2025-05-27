import pandas as pd

# 读取两个 Excel 文件
df1 = pd.read_excel("C:/Users/Administrator/Desktop/full.xls")  # 表1：包含完整信息        
df2 = pd.read_excel("C:/Users/Administrator/Desktop/临时表.xlsx")  # 表2：需要匹配信息

# 在合并之前添加这些代码来查看实际的列名
print("df1的列名:", df1.columns.tolist())
print("df2的列名:", df2.columns.tolist())

# 根据姓名列进行匹配
merged_df = pd.merge(df2, df1, on="姓名", how="left")

try:
    merged_df.to_excel("C:/Users/Administrator/Desktop/匹配结果.xlsx", index=False)
    print("匹配完成，结果已保存到 '匹配结果.xlsx'")
except Exception as e:
    print(f"保存文件时出错：{e}")