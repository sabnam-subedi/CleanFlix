
# Import required libraries
import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import os

df=pd.read_csv("../data/raw/netflix_titles.csv")

duplicate_rows = df[df.duplicated()]
print(f"Duplicate rows: {duplicate_rows.shape[0]}")


missing = df.isnull().sum()
missing_percent = (missing / len(df)) * 100

missing_summary = pd.DataFrame({
    'Missing Values': missing,
    'Missing %': missing_percent.round(2)
})

print(missing_summary[missing_summary['Missing Values'] > 0])

df["director"]=df["director"].fillna("Unknown")

df["cast"]=df['cast'].fillna('No Cast listed')

df['country']=df['country'].fillna('Not Available')

df['date_added']=df['date_added'].fillna('Not Mentioned')

df['rating']=df['rating'].fillna('not rated')

print(df[df['rating'].isna()]['rating'])

missing_duration_info = df[df['duration'].isnull()][['title', 'type', 'duration']]

print(missing_duration_info) 

df[['duration_time', 'duration_unit']] = df['duration'].str.extract(r'(\d+)\s*(\D+)')

df['duration_time'] = pd.to_numeric(df['duration_time'], errors='coerce')

movie_avg = round(df.loc[df['type'] == 'Movie', 'duration_time'].mean())

df.loc[(df['type'] == 'Movie') & (df['duration_time'].isna()), 'duration_time'] = movie_avg

df.loc[(df['type'] == 'Movie') & (df['duration_unit'].isna()), 'duration_unit'] = 'min'

df['duration'] = df['duration_time'].astype(int).astype(str) + ' ' + df['duration_unit']

text_columns = ['title', 'director', 'cast', 'country', 'rating']
for col in text_columns:
    df[col] = df[col].str.strip().str.lower()

invalid_ratings = ['74 min', '84 min', '66 min']
df = df[~df['rating'].isin(invalid_ratings)]
rating_map = {
    'nr': 'not rated',
    'ur': 'not rated',
    'not rated': 'not rated',  
    'tv-y7-fv': 'tv-y7-fv'    
}
df['rating'] = df['rating'].replace(rating_map)

print(df['rating'].unique())

df['country'].value_counts()

df['rating'] = df['rating'].astype('category')

rating_order =rating_order =['pg-13','tv-ma', 'pg','tv-14','tv-pg' , 'tv-y' , 'tv-y7',  'r' , 'tv-g' , 'g' ,  'nc-17' , 'not rated',  'tv-y7-fv']

rating_dtype = CategoricalDtype(categories=rating_order, ordered=True)

df['rating'] = df['rating'].astype(rating_dtype)
missing = df.isnull().sum()
print(missing)
df_cleaned=df

output_path = os.path.join('..', 'data', 'cleaned', 'netflix_cleaned.xlsx')

df_cleaned.to_excel(output_path, index=False)










      






