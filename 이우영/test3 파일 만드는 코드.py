import pandas as pd
# test 2 코드
# 1. Load test.csv
df_test = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\test.csv")

# 2. Convert '측정일시' to datetime objects
df_test['측정일시'] = pd.to_datetime(df_test['측정일시'])

# 3. Extract date/time components
df_test['month'] = df_test['측정일시'].dt.month
df_test['day'] = df_test['측정일시'].dt.day
df_test['hour'] = df_test['측정일시'].dt.hour
df_test['minute'] = df_test['측정일시'].dt.minute

# 4. Create the final '작업휴무' column based on the rule:
#    If ALL '작업유형' values for a specific day are 'Light_Load', then '휴무', else '가동'.
daily_work_status = df_test.groupby('day')['작업유형'].transform(lambda x: (x == 'Light_Load').all())

# 5. Apply the determined status to the new '작업휴무' column
df_test['작업휴무'] = daily_work_status.apply(lambda x: '휴무' if x else '가동')

# 6. Save the processed DataFrame to a new CSV file
# output_filename = 'test_processed.csv'



# df_sorted = df_test.sort_values(by='측정일시').reset_index(drop=True)
df_test.to_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\test2.csv", index=False, encoding="utf-8-sig")



# test 3 만드는 코드


# 1. Load the training data and create the most accurate pattern database (Method 2: All months)
df_train = pd.read_csv("C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\train_df.csv")
GROUPING_KEYS = ['작업휴무', '작업유형', '시간분']

# Create Pattern DB
pf_pattern_db = df_train.groupby(GROUPING_KEYS).agg(
    impute_lagging_pf=('지상역률(%)', 'mean'),
    impute_leading_pf=('진상역률(%)', 'mean')
).reset_index()


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
 
df_test_imputed.to_csv('C:\\Users\\USER\\Desktop\\electric_power_-team\\data\\test3.csv', index=False, encoding="utf-8-sig")
