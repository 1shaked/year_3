import matplotlib.pyplot as plt
import statistics as stats
import pandas as pd

df = pd.read_excel('QualityControl/ex1q1.xlsx')
df = df[df.columns[0:7]]
df.drop(df.columns[0], axis=1, inplace=True)
df.rename(columns={'std s': 'std', }, inplace=True  )
print(df)

A3 = 1.427
B4 = 2.089

ucl_x = df['mean'].mean() + 3 * df['mean'].std() * A3
lcl_x = df['mean'].mean() - 3 * df['mean'].std() * A3

ucl_s = df['std'].mean() * B4
lcl_s = 0

plt.axhline(y=ucl_x, color='r', linestyle='--', label='UCL')
plt.axhline(y=lcl_x, color='r', linestyle='--', label='LCL')
plt.axhline(y=df['mean'].mean(), color='g', linestyle='-', label='Mean')
plt.plot(df['mean'], label='Mean')
plt.title('Mean Chart')
plt.show()

plt.axhline(y=ucl_s, color='r', linestyle='--', label='UCL')
plt.axhline(y=lcl_s, color='r', linestyle='--', label='LCL')
plt.axhline(y=df['std'].mean(), color='g', linestyle='-', label='Mean')
plt.plot(df['std'], label='Std')
plt.title('Std Chart')
plt.show()
