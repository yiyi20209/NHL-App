import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from collections import Counter
import seaborn as sn
import pickle
import os
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from tidyData import tidy_data, split_data
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split


def preprocess(df, split=True):
    train_val_df, test_df = split_data(df)

    ## Selecting only the columns from Q4
    columns = ['game_period', 'x', 'y', 'distanceNet_or_shotDistance', 'goal', 'shot_angle_absolute', 
               'shotType', 'last_event', 'last_x', 'last_y', 'game_seconds', 'time_from_last_event', 
               'distance_from_last_event', 'rebound', 'speed', 'time_since_powerplay_started', 
               'nbFriendly_non_goalie_skaters', 'nbOpposing_non_goalie_skaters', 'change_in_shot_angle']

    data = train_val_df[columns]


    ## Proper datatype casting of columns
    cols_dtype_change = ['x', 'y', 'last_x', 'last_y', 'distance_from_last_event', 
                         'speed', 'sum_x', 'distanceNet_or_shotDistance']
    for col in cols_dtype_change:
        if col in data.columns:
            data[col] = data[col].astype('float')
        if 'game_period' in data.columns:
            data['game_period'] = data['game_period'].astype('str')


    cat_cols = data.select_dtypes(exclude="number").columns
    num_cols = data.select_dtypes(include="number").columns


    feature_n = columns[:]
    feature_names = []
    for feature in cat_cols:
        if feature in cat_cols:
            # print(data[feature].unique())
            if feature == 'shotType':
                # print(feature, len(train_val_df[feature].unique()) - 1)            
                feature_names.extend([feature]*(len(train_val_df[feature].unique()) - 1))
            else:
                # print(feature, len(train_val_df[feature].unique()))            
                feature_names.extend([feature]*(len(train_val_df[feature].unique())))            
        else:
            feature_names.append(feature)

    # print(feature_names, len(feature_names))
    num = SimpleImputer(strategy="mean").fit_transform(data[num_cols])
    # num = StandardScaler().fit_transform(num)
    cat = SimpleImputer(strategy="most_frequent").fit_transform(data[cat_cols])
    cat = SimpleImputer(missing_values=None,strategy="most_frequent").fit_transform(cat)
    cat = OneHotEncoder(handle_unknown="ignore", sparse=False).fit_transform(cat)
    data = pd.concat((pd.DataFrame(num, columns=list(num_cols)), 
                      pd.DataFrame(cat, columns=feature_names)), 
                      axis=1, names = list(num_cols).extend(list(cat_cols)))
    # print(data)


    ## Train-val splitting
    if split==True:
        return train_test_split(data.loc[::,data.columns!='goal'],
                                                         data[['goal']],
                                                         test_size=0.25,
                                                         random_state=10, 
                                                         shuffle = True)
        # return X_train, X_val, y_train, y_val
    else:
        return data

def transform(X_train, X_val, y_train):
    # Using the mask of features selected from training data
    # Check `AdvancedModel.ipynb` to verify selected features
    features = X_val.loc[::,X_val.columns!='goal'].loc[:,[False,  True,  
        True,  True,  True, False,  True,  True,  True,  True,  True,  
        True,  True,  True,  True,  True,  True,  True,  True,  True,  
        True, False,  True,  True,  True,  True,  True, True, False, 
        False, False,  True,  True, False, False, False, False, False, 
        False, False,  True,  True,  True, False,  True]]
    return features