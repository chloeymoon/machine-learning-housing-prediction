import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import seaborn as sns
from scipy.stats import norm
from scipy.stats import skew
from scipy.special import boxcox1p
from scipy.stats import boxcox_normmax
from sklearn.preprocessing import StandardScaler
from scipy import stats


def clean(df):
  # **** what to do with Year and Month?
  for var in ['MSSubClass']:
      # later on, change to the actual string values
      df[var] = df[var].apply(str)

  # no garage, no bathrooms, etc., based on data description?
  for col in ('GarageYrBlt', 'GarageArea', 'GarageCars','MasVnrArea','BsmtFinSF1','BsmtFinSF2'
         ,'BsmtFullBath','BsmtHalfBath','FullBath','HalfBath','BsmtUnfSF','TotalBsmtSF'):
      df[col] = df[col].fillna(0).astype(int)

  # Replacing missing data with None, based on data description
  for col in ['GarageType', 'GarageFinish', 'GarageQual', 'GarageCond','BsmtQual',
          'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2',"PoolQC"
         ,'Alley','Fence','MiscFeature','FireplaceQu','MasVnrType','Utilities']:
      df[col] = df[col].fillna('None')

  # Home functionality (Assume typical unless deductions are warranted):
  # data description says NA means typical
  df['Functional'] = df['Functional'].fillna('Typ')

  # lot frontage: correlated with lot area (0.48) and neighborhoods (domain expertise)
  df = cleanLotFrontage(df)

  # ****** MSZoning, grouped by MSSubClass but I'm not exactly sure this is valid
  # did chi square test, wasn't too helpful, so many other categorical variables associated as much
  df['MSZoning'] = df.groupby('MSSubClass')['MSZoning'].transform(lambda x: x.fillna(x.mode()[0]))

  common_vars = ['Exterior1st','Exterior2nd','SaleType','Electrical','KitchenQual']
  for var in common_vars:
      df[var] = df[var].fillna(df[var].mode()[0])

  return df

def cleanLotFrontage(df):
  df['LotArea_bin'] = pd.cut(df['LotArea'],50).apply(lambda x: x.mid)
  df['Lotfrontage_grouped'] = df.groupby(['Neighborhood','LotArea_bin'])['LotFrontage'].transform(lambda x: x.fillna(x.median()))
  df['Lotfrontage_grouped'] = df.groupby(['Neighborhood'])['LotFrontage'].transform(lambda x: x.fillna(x.median()))
  #df['LotFrontage_neigh'] = df.groupby('Neighborhood')['LotFrontage'].transform(lambda x: x.fillna(x.median()))
  #df['LotFrontage_lotarea'] = df.groupby('LotArea')['LotFrontage'].transform(lambda x: x.fillna(x.median()))
  df['LotFrontage'] = df['Lotfrontage_grouped']
  df = df.drop(columns=['LotArea_bin','Lotfrontage_grouped'])
  return df

def computeMissingness(df):
  total = df.isnull().sum().sort_values(ascending=False)
  percent = (df.isnull().sum()/df.isnull().count()).sort_values(ascending=False)
  missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
  # df.boxplot(column='LotFrontage',by='Neighborhood')
  # plt.scatter(x=df.LotArea,y=df.LotFrontage)
  return missing_data

# helper function to visualize distribution
def visdist(df,col):
  plt.subplot(1, 2, 1)
  plt.hist(df[col])
  plt.subplot(1, 2, 2)
  plt.scatter(df[col],df['SalePrice'])
  plt.tight_layout()
  plt.show()
