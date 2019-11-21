import os
import glob
import pandas as pd
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
plt.style.use('fivethirtyeight')
mpl.rcParams['patch.linewidth'] = 0

# Get data
path = "./pm25_usembassy"
extension = 'csv'
os.chdir(path)

files = sorted(glob.glob('*.{}'.format(extension)))
df = pd.DataFrame()

for idx, file in enumerate(files):
    if idx > 1:
        rows = 2
    else:
        rows = 4

    df = df.append(pd.read_csv(file,
                               sep=',',
                               encoding = 'ISO-8859-1',
                               skiprows=rows,
                               usecols=['Date (LST)', 'Value', 'AQI'],
                               parse_dates=['Date (LST)']
                               ),
                   ignore_index=True)

df = df.set_index('Date (LST)')
df['Value'] = df['Value'] * 1000

# Get daily average
df_avg = df.resample('D').mean()
df_avg['Year'] = df_avg.index.year
df_avg['Month'] = df_avg.index.month
df_avg['Day'] = df_avg.index.day
df_avg['MonthDay'] = '2019/' + df_avg.index.strftime('%b') + '/' + df_avg['Day'].astype(str)

# Get sub-data: October and November
df_avg_sub = df_avg.loc[((df_avg['Month'] == 11) & (df_avg['Day'] <= 19)) | (df_avg['Month'] == 10)]
df_avg_sub['MonthDay'] = pd.to_datetime(df_avg_sub['MonthDay'], format='%Y/%b/%d')

# Group by year
value2015 = df_avg_sub.loc[df_avg_sub['Year'] == 2015, ['MonthDay', 'Value']].set_index('MonthDay').rename(columns={'Value': 'Value2015'})
value2016 = df_avg_sub.loc[df_avg_sub['Year'] == 2016, ['MonthDay', 'Value']].set_index('MonthDay').rename(columns={'Value': 'Value2016'})
value2017 = df_avg_sub.loc[df_avg_sub['Year'] == 2017, ['MonthDay', 'Value']].set_index('MonthDay').rename(columns={'Value': 'Value2017'})
value2018 = df_avg_sub.loc[df_avg_sub['Year'] == 2018, ['MonthDay', 'Value']].set_index('MonthDay').rename(columns={'Value': 'Value2018'})
value2019 = df_avg_sub.loc[df_avg_sub['Year'] == 2019, ['MonthDay', 'Value']].set_index('MonthDay').rename(columns={'Value': 'Value2019'})

df_prep = pd.concat([value2015, value2016, value2017, value2018, value2019], axis=1)
df_prep['base_min'] = df_prep[['Value2015', 'Value2016', 'Value2017', 'Value2018']].min(axis=1)
df_prep['base_max'] = df_prep[['Value2015', 'Value2016', 'Value2017', 'Value2018']].max(axis=1)
df_prep['base_median'] = df_prep[['Value2015', 'Value2016', 'Value2017', 'Value2018']].median(axis=1)

# Plot
fig, ax = plt.subplots(figsize=(12, 8))

ax.fill_between(df_prep.index.values,
                df_prep['base_min'].values,
                df_prep['base_max'].values,
                color='#D7E7EE')        

ax.plot(df_prep.index.values,
        df_prep['base_median'].values,
        color='#5099B5', linewidth=2.5)

ax.plot(df_prep.index.values,
        df_prep['Value2019'].values,
        color='#E85051', linewidth=2.5)

plt.ylabel("µg/m³ (24-hour mean)", fontsize=16, labelpad=10)
plt.xlim(['2019/Sep/30', '2019/Nov/20'])

ax.xaxis.set_major_locator(MultipleLocator(7))
ax.xaxis.set_major_formatter(DateFormatter("%b/%d"))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.tick_params(axis = 'both', which = 'major', labelsize = 16)
ax.axhline(y=25, color='black', linewidth=1, alpha=0.4, linestyle='--', dashes=(5, 10))
ax.xaxis.label.set_visible(False)

# Adding a title and a subtitle
ax.text(x='2019/Sep/26', y = 245, s = "Government ban on raw coal comes into effect",
        fontsize=28, weight='bold', alpha=0.75)
ax.text(x='2019/Sep/26', y=230,
        s='PM 2.5 levels in 2019 have been lower than 2015-2018\'s levels in Ulaanbaatar',
        fontsize=18, alpha=0.85)

# Annotations
ax.text(x='2019/Sep/26', y=-35, s = '                                                                                                                                    Source: https://www.stateair.mn   ', 
        fontsize = 14, color = 'grey', alpha=0.7)
ax.text(x='2019/Nov/01', y = 90, s="  Median\n2015-2018",
        fontsize=12, weight='bold', color='#5099B5')
ax.text(x='2019/Oct/13', y = 64, s="2019",
        fontsize=12, weight='bold', color='#E85051')
ax.text(x='2019/Oct/23', y = 160, s="   Range\n2015-2018 ---------------o",
        fontsize=12, color='#5099B5')
ax.text(x='2019/Nov/13', y = 15, s="WHO guideline",
        fontsize=12, color='black', alpha=0.4)        

fig.tight_layout()
plt.savefig("UB_PM25.png", bbox_inches='tight')
plt.show()
