import pandas as pd

df_excel = pd.read_excel("test.xlsx", sheet_name="Лист1", engine="openpyxl")
df_excel.to_csv("output.csv", encoding='utf-8')
print(df_excel.head())