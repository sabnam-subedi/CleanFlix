
# Import libraries
import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np

# Load the dataset from raw folder
df=pd.read_csv("../data/raw/netflix_titles.csv")

# Check for duplicates
duplicate_rows = df[df.duplicated()]
print(f"Duplicate rows: {duplicate_rows.shape[0]}")

# Check for missing values
missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100

# Show missing summary
missing_summary = pd.DataFrame({
    'Missing Values': missing,
    'Missing %': missing_percent.round(2)
})

print(missing_summary[missing_summary['Missing Values'] > 0])

# Dealing with missing values

# use of .fillna to add values to null columns

df["director"]=df["director"].fillna("Unknown")

df["cast"]=df['cast'].fillna('No Cast listed')

df['country']=df['country'].fillna('Not Available')

# Converting to panda data-time

# errors='coerce' will replace any value having incorrect formatting with missing datetime

df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

#timestamp= pandas’ equivalent of Python’s datetime.datetime

df['date_added'] = df['date_added'].fillna(pd.Timestamp('2000-01-01'))

df['rating']=df['rating'].fillna('Not rated')

#checking the information of missing duration 

missing_duration_info = df[df['duration'].isnull()][['title', 'type', 'duration']]

print(missing_duration_info)

#converting the duration to two separate types 

df[['duration_time', 'duration_unit']] = df['duration'].str.extract(r'(\d+)\s*(\D+)')


#converting to numeric values

df['duration_time'] = pd.to_numeric(df['duration_time'], errors='coerce')

#calculating average duration of movie

movie_avg = round(df.loc[df['type'] == 'Movie', 'duration_time'].mean())

#adding missing value for movies

df.loc[(df['type'] == 'Movie') & (df['duration_time'].isna()), 'duration_time'] = movie_avg

df.loc[(df['type'] == 'Movie') & (df['duration_unit'].isna()), 'duration_unit'] = 'min'

#combininb different data types for duration

df['duration'] = df['duration_time'].astype(int).astype(str) + ' ' + df['duration_unit']

#Formatting and Data consistency check

#accessing to column for spacing and cases to avoid unnecessary unique values

text_columns = ['title', 'director', 'cast', 'country', 'rating']
for col in text_columns:
    df[col] = df[col].str.strip().str.lower()

#unique values for rating and country

df['rating'].unique()

df['country'].value_counts()

#converting rating datatype from string to category/groupby

df['rating'] = df['rating'].astype('category')

#arranging rating in customized order
rating_order = ['g', 'pg', 'pg-13', 'r', 'nc-17', 'tv-14', 'tv-ma', 'not rated']
rating_dtype = CategoricalDtype(categories=rating_order, ordered=True)

# assigning the order to the column
df['rating'] = df['rating'].astype(rating_dtype)









      






