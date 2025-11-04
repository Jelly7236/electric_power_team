import pandas as pd
import numpy as np

train_df = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\train_df.csv")


# Filter 1: iso_week is 1 or 2
# filter_iso_week = train_df['iso_week'].isin([1, 2])

# Filter 2: month is 3 or 11
filter_month = train_df['month'].isin([3, 4, 5, 10, 11])

# Combine the filters using the OR operator (|)
df_filtered = train_df[filter_month].copy()

# 1. Convert '측정일시' to datetime objects
df_filtered['측정일시'] = pd.to_datetime(df_filtered['측정일시'])

# 2. Sort the DataFrame by '측정일시'
# df_sorted = df_filtered.sort_values(by='측정일시').reset_index(drop=True)

GROUPING_KEYS = ['작업휴무', '작업유형', '시간분']

# Create Pattern DB
pf_pattern_db = df_filtered.groupby(GROUPING_KEYS).agg(
    impute_lagging_pf=('지상역률(%)', 'mean'),
    impute_leading_pf=('진상역률(%)', 'mean')
).reset_index()


pf_pattern_db



# 2. Load the processed test data (test2.csv)
df_test = pd.read_csv('C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\test2.csv')

# 3. Prepare the test data for merging: Calculate '시간분'
df_test['시간분'] = df_test['hour'] + df_test['minute'] / 60


# 4. Merge (붙이기) the test data with the pattern database
df_test_imputed = df_test.merge(
    pf_pattern_db, 
    on=GROUPING_KEYS, 
    how='left'
)

# 5. Impute the missing 역률 columns (지상역률, 진상역률)
# If the target columns don't exist, they are created and filled with imputed values.
if '지상역률(%)' not in df_test_imputed.columns:
    df_test_imputed['지상역률(%)'] = df_test_imputed['impute_lagging_pf']
else:
    df_test_imputed['지상역률(%)'] = df_test_imputed['지상역률(%)'].fillna(df_test_imputed['impute_lagging_pf'])

if '진상역률(%)' not in df_test_imputed.columns:
    df_test_imputed['진상역률(%)'] = df_test_imputed['impute_leading_pf']
else:
    df_test_imputed['진상역률(%)'] = df_test_imputed['진상역률(%)'].fillna(df_test_imputed['impute_leading_pf'])


# 6. Clean up the DataFrame: Drop the temporary imputation columns
df_test_imputed.drop(columns=['impute_lagging_pf', 'impute_leading_pf'], inplace=True)

# 7. Save the final imputed DataFrame
 
df_test_imputed.to_csv('C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\test4.csv', index=False, encoding="utf-8-sig")

df_test_imputed.info()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the imputed test data (test3.csv)
df_test = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\test4.csv")

# 2. Filter data by work status
df_on = df_test[df_test['작업휴무'] == '가동'].copy()
df_off = df_test[df_test['작업휴무'] == '휴무'].copy()

# 3. Set visualization style and define constants
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False 

LAGGING_CRITERION = 90
LEADING_CRITERION = 95
LAGGING_REG_START = 9
LAGGING_REG_END = 22

# 4. Create 1x2 subplots
fig, axes = plt.subplots(1, 2, figsize=(18, 6), sharey=True)
fig.suptitle('12월 예측 역률: 작업휴무 별 지상/진상 역률 사이클 비교', fontsize=18, y=1.05)

# --- Plotting Function for Single Status ---
def plot_pf_cycle(data, status, ax, show_legend=True):
    # Melt the data to combine Lagging and Leading Power Factors
    df_melted = data.melt(
        id_vars=['시간분'],
        value_vars=['지상역률(%)', '진상역률(%)'],
        var_name='역률종류',
        value_name='역률(%)'
    )
    
    # Plotting
    sns.lineplot(
        data=df_melted, 
        x='시간분', 
        y='역률(%)', 
        hue='역률종류', 
        ax=ax,
        palette={'지상역률(%)': 'blue', '진상역률(%)': 'green'},
        linewidth=2
    )
    
    # Criteria and Regulation
    ax.axhline(y=LAGGING_CRITERION, color='r', linestyle=':', alpha=0.6, label='지상역률 기준선 (90%)')
    ax.axhline(y=LEADING_CRITERION, color='g', linestyle=':', alpha=0.6, label='진상역률 기준선 (95%)')
    ax.axvspan(LAGGING_REG_START, LAGGING_REG_END, color='yellow', alpha=0.15, label='지상역률 규제 시간')
    ax.axvspan(22, 24, color='lightgreen', alpha=0.15, label='진상역률 규제 시간')
    ax.axvspan(0, 9, color='lightgreen', alpha=0.15)
    
    ax.set_title(f'① {status} 시 예측 역률', fontsize=16)
    ax.set_xlabel('시간 (Hour, 15분 단위)', fontsize=12)
    ax.set_ylabel('역률(%)', fontsize=12)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 105)
    
    if show_legend:
        # Customizing legend to show only PF types
        h, l = ax.get_legend_handles_labels()
        custom_handles = [h[0], h[1]]
        custom_labels = ['지상역률(%)', '진상역률(%)']
        ax.legend(custom_handles, custom_labels, title='역률 종류', loc='lower right')
    else:
        ax.get_legend().remove()
        ax.set_ylabel('')

# 5. Plot 1: '가동' 상태
plot_pf_cycle(df_on, '가동', axes[0], show_legend=True)


# 6. Plot 2: '휴무' 상태
plot_pf_cycle(df_off, '휴무', axes[1], show_legend=False)


plt.tight_layout()
plt.savefig('imputed_pf_cycle_on_off_separate.png')
plt.close()