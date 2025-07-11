
# Import required libraries
import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import os
import matplotlib.pyplot as plt

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

df['country'] = df['country'].apply(lambda x: x.split(',')[0].strip())
multi_country_rows = df[df['country'].notna() & df['country'].str.contains(',')]
print(f"Number of rows with multiple countries: {multi_country_rows.shape[0]}")
print(df.describe())
 
df_cleaned=df


output_path = os.path.join('..', 'data', 'cleaned', 'netflix_cleaned.xlsx')
df_cleaned.to_excel(output_path, index=False)

country_counts = df_cleaned['country'].value_counts()
#print(country_counts)

df_cleaned['country_grouped'] = df_cleaned['country'].apply(
    lambda x: x if country_counts[x] > 200 else 'Others')

final_country_counts = df_cleaned['country_grouped'].value_counts()
country_dict = final_country_counts.to_dict()
print(country_dict)

others_count = country_dict.pop("Others", 0)
labels = list(country_dict.keys()) + ["Others"]
sizes = list(country_dict.values()) + [others_count]


wp = {'linewidth': 1.5, 'edgecolor': "white"}

fig, ax = plt.subplots(figsize=(15, 10))
wedges,texts, autotexts = ax.pie(sizes,
                                   
                                 autopct='%1.1f%%',
                                  labels=labels,
                                  shadow=False,
                                
                                  startangle=0,
                                  wedgeprops=wp,
                                  textprops=dict(color="black"))

others_count = df_cleaned[df_cleaned['country_grouped'] == 'Others']['country'].unique()


others_count_sorted = sorted(others_count)
others_text = "\n".join(others_count_sorted)

plt.gcf().text(
    0.005, 0.005, 
    "Grouped under 'Others':\n" + others_text,
    fontsize=6,
    verticalalignment='bottom',
    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1')
)   

plt.setp(autotexts, size=5, weight="regular")
ax.set_title(" Origin of different movies with (Others) representing the rare countries")
plt.show()
 

type_counts= df_cleaned["type"].value_counts()
print(type_counts)

labels = type_counts.index.tolist()
values = type_counts.values.tolist()
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(labels, values, color=['blue', 'orange'])
ax.set_title("Distribution of Movies and TV Shows")
ax.set_xlabel("Type")
ax.set_ylabel("Count of Movies and TV-shows")

plt.show()

top_countries = df_cleaned['country_grouped'].value_counts().head(5).index

df_top = df_cleaned[
    (df_cleaned['country_grouped'].isin(top_countries)) & 
    (df_cleaned['country_grouped'] != 'Others')
]
colors = [
    'blue',  
    'orange', 
    'green',  
    'red',  
    'purple',  
    'brown',  
    'pink',  
    'gray',  
    'indigo',  
    'cyan',  
    'magenta',  
    'turquoise',  
    'maroon'   
]
pivot = pd.pivot_table(
    df_top, 
    index='country_grouped', 
    columns='rating', 
    values='title', 
    aggfunc='count', 
    fill_value=0
)
color_subset = colors[:pivot.shape[1]]
pivot.plot(kind='bar', figsize=(12, 8), width=0.5,color=color_subset,)
plt.title("Ratings Distribution by Country (Top 5 Countries, Filtered Ratings)")
plt.xlabel("Country")
plt.ylabel("Number of Titles")
plt.xticks(rotation=0)
plt.legend(title="Rating", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

release_trend = df_cleaned['release_year'].value_counts().sort_index()
plt.figure(figsize=(15, 8))
plt.plot(release_trend.index, release_trend.values, color='#cfb8e6', linewidth=2, label='Total Titles')

plt.scatter(release_trend.index, release_trend.values, marker="o",color='#9b6be8', s=30, zorder=3, label='Yearly Data Points')


plt.title(" Netflix Movies' Release Trend by Year")
plt.xlabel("Release Year")
plt.ylabel("Number of Movies")
plt.grid(True, linestyle='--', alpha=0.6)
plt.xticks(rotation=45)
plt.legend()
plt.show()

df_filtered = df_cleaned[df_cleaned['type'].isin(['Movie'])]
avg_duration = df_filtered.groupby(['release_year', 'type'])['duration_time'].mean().reset_index()

pivot_avg = avg_duration.pivot(index='release_year', columns='type', values='duration_time')
pivot_avg = pivot_avg[pivot_avg.index>1940] 

plt.figure(figsize=(12, 6))
plt.plot(pivot_avg.index, pivot_avg['Movie'], marker='o', label='Avg Movie Duration (min)', color='blue')


plt.title("Average Movie Duration by Year")
plt.xlabel("Release Year after 1940")
plt.ylabel("Average Duration in min ")
plt.grid(True, linestyle='--', alpha=0.5)
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()














      






