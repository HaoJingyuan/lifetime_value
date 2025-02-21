from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import os
import numpy as np
import pandas as pd
import tqdm
import multiprocessing

pd.options.mode.chained_assignment = None  # default='warn'


COMPANYS = [
    10000, 101200010, 101410010, 101600010, 102100020, 102700020,
    102840020, 103000030, 103338333, 103400030, 103600030,
    103700030, 103800030, 104300040, 104400040, 104470040,
    104900040, 105100050, 105150050, 107800070
]

def load_data(company):
  all_data_filename = r'D:\github_repo_forked\lifetime_value\acquire-valued-shoppers-challenge\transactions.csv\transactions.csv'
  one_company_data_filename = (
      r'D:\github_repo_forked\lifetime_value\acquire-valued-shoppers-challenge\transactions_company_{}.csv'
      .format(company))
  if os.path.isfile(one_company_data_filename):
    df = pd.read_csv(one_company_data_filename)
  else:
    data_list = []
    chunksize = 10**6
    # 350 iterations
    for chunk in tqdm.tqdm(pd.read_csv(all_data_filename, chunksize=chunksize)):
      data_list.append(chunk.query(f'company=={company}'))
    df = pd.concat(data_list, axis=0)
    df.to_csv(one_company_data_filename, index=None)
  return df

def preprocess(df):
  df = df.query('purchaseamount>0')
  df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
  df['start_date'] = df.groupby('id')['date'].transform('min')

  # Compute calibration values
  calibration_value = (
      df.query('date==start_date').groupby('id')
      ['purchaseamount'].sum().reset_index())
  calibration_value.columns = ['id', 'calibration_value']

  # Compute holdout values
  one_year_holdout_window_mask = (
      (df['date'] > df['start_date']) &
      (df['date'] <= df['start_date'] + np.timedelta64(365, 'D')))
  holdout_value = (
      df[one_year_holdout_window_mask].groupby('id')
      ['purchaseamount'].sum().reset_index())
  holdout_value.columns = ['id', 'holdout_value']

  # Compute calibration attributes
  calibration_attributes = (
      df.query('date==start_date').sort_values(
          'purchaseamount', ascending=False).groupby('id')[[
              'chain', 'dept', 'category', 'brand', 'productmeasure'
          ]].first().reset_index())

  # Merge dataframes
  customer_level_data = (
      calibration_value.merge(calibration_attributes, how='left',
                              on='id').merge(
                                  holdout_value, how='left', on='id'))
  customer_level_data['holdout_value'] = (
      customer_level_data['holdout_value'].fillna(0.))
  categorical_features = ([
      'chain', 'dept', 'category', 'brand', 'productmeasure'
  ])
  customer_level_data[categorical_features] = (
      customer_level_data[categorical_features].fillna('UNKNOWN'))

  # Specify data types
  customer_level_data['log_calibration_value'] = (
      np.log(customer_level_data['calibration_value']).astype('float32'))
  customer_level_data['chain'] = (
      customer_level_data['chain'].astype('category'))
  customer_level_data['dept'] = (customer_level_data['dept'].astype('category'))
  customer_level_data['brand'] = (
      customer_level_data['brand'].astype('category'))
  customer_level_data['category'] = (
      customer_level_data['category'].astype('category'))
  customer_level_data['label'] = (
      customer_level_data['holdout_value'].astype('float32'))
  return customer_level_data

def process(company):
  print("Process company {}".format(company))
  transaction_level_data = load_data(company)
  customer_level_data = preprocess(transaction_level_data)
  customer_level_data_file = (
      r'D:\github_repo_forked\lifetime_value\acquire-valued-shoppers-challenge\customer_level_data_company_{}.csv'
      .format(company))
  customer_level_data.to_csv(customer_level_data_file, index=None)
  print("Done company {}".format(company))

# print("cpu count",multiprocessing.cpu_count())
# p = multiprocessing.Pool(multiprocessing.cpu_count())
# _ = p.map(process, COMPANYS)

# for company in COMPANYS:
#     process(company)

def load_100_data(company):
    all_data_filename = r'D:\github_repo_forked\lifetime_value\acquire-valued-shoppers-challenge\transactions.csv\transactions.csv'
    one_company_data_filename = (
        r'D:\github_repo_forked\lifetime_value\acquire-valued-shoppers-challenge\transactions_company_{}.csv'
        .format(company))
    
    df = pd.read_csv(all_data_filename, nrows=100)  # 只读取前100行
    print(df.columns)
    print(df['company'].dtype)

    data_list = []
    print('query:',f"company=={company}")
    data_list.append(df.query(f'company=={company}'))
    print(data_list)
    df = pd.concat(data_list, axis=0)
    df.to_csv(one_company_data_filename, index=None)

    return df

if __name__ == '__main__':
    # 创建一个进程池，使用所有可用的CPU核心
    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        # 使用进程池并行执行process函数，传入COMPANYS列表中的每个公司
        p.map(process, COMPANYS)
