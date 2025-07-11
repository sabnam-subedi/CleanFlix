# app.py
from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
from pandas.api.types import CategoricalDtype
import numpy as np
import matplotlib
matplotlib.use('Agg')  

import matplotlib.pyplot as plt


app = Flask(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(base_dir, 'static', 'data')
plots_folder = os.path.join(base_dir, 'static', 'plots')
os.makedirs(os.path.join(data_folder, 'cleaned'), exist_ok=True)
os.makedirs(os.path.join(plots_folder), exist_ok=True)

cleaned_path = os.path.join(data_folder, 'cleaned', 'netflix_cleaned.xlsx')

if os.path.exists(cleaned_path):
    df_cleaned = pd.read_excel(cleaned_path)
else:
    raw_path = os.path.join(data_folder, 'raw', 'netflix_titles.csv')
    df = pd.read_csv(raw_path)

    df["director"] = df["director"].fillna("Unknown")
    df["cast"] = df['cast'].fillna('No Cast listed')
    df['country'] = df['country'].fillna('Not Available')
    df['date_added'] = df['date_added'].fillna('Not Mentioned')
    df['rating'] = df['rating'].fillna('not rated')

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
    df['rating'] = df['rating'].replace({
        'nr': 'not rated', 'ur': 'not rated', 'not rated': 'not rated', 'tv-y7-fv': 'tv-y7-fv'
    })

    rating_order = ['pg-13','tv-ma', 'pg','tv-14','tv-pg','tv-y','tv-y7','r','tv-g','g','nc-17','not rated','tv-y7-fv']
    rating_dtype = CategoricalDtype(categories=rating_order, ordered=True)
    df['rating'] = df['rating'].astype(rating_dtype)

    df['country'] = df['country'].apply(lambda x: x.split(',')[0].strip())

    df.to_excel(cleaned_path, index=False)
    df_cleaned = df

columns = df_cleaned.columns.tolist()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/data')
def show_cleaned_data():
    return render_template("data.html", columns=columns)

@app.route('/api/data')
def api_data():
    draw = int(request.args.get('draw', 1))
    start = int(request.args.get('start', 0))
    length = int(request.args.get('length', 10))
    data_slice = df_cleaned.iloc[start:start + length]
    data_json = data_slice.to_dict(orient='records')
    return jsonify({
        'draw': draw,
        'recordsTotal': len(df_cleaned),
        'recordsFiltered': len(df_cleaned),
        'data': data_json
    })

@app.route('/raw')
def show_raw_data():
    raw_path = os.path.join(data_folder, 'raw', 'netflix_titles.csv')
    df_raw = pd.read_csv(raw_path)
    table = df_raw.to_html(classes="display", index=False)
    return render_template('raw.html', table=table)

@app.route('/plots')
def plots():
    country_counts = df_cleaned['country'].value_counts()
    df_cleaned['country_grouped'] = df_cleaned['country'].apply(lambda x: x if country_counts.get(x, 0) > 200 else 'Others')

    final_country_counts = df_cleaned['country_grouped'].value_counts()
    country_dict = final_country_counts.to_dict()

    others_count = country_dict.pop("Others", 0)
    labels = list(country_dict.keys()) + ["Others"]
    sizes = list(country_dict.values()) + [others_count]

    fig, ax = plt.subplots(figsize=(15, 10))
    wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', labels=labels, startangle=0,
                                      wedgeprops={'linewidth': 1.5, 'edgecolor': "white"},
                                      textprops=dict(color="black"))
    others_names = sorted([str(c) for c in df_cleaned[df_cleaned['country_grouped'] == 'Others']['country'].unique()])

    plt.gcf().text(0.005, 0.005, "Grouped under 'Others':\n" + "\n".join(others_names),
                  fontsize=6, verticalalignment='bottom',
                  bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1'))
    plt.setp(autotexts, size=5)
    ax.set_title("Origin of Movies (Rare Countries Grouped as 'Others')")
    plt.savefig(os.path.join(plots_folder, 'country_pie_chart.png'), bbox_inches='tight')
    plt.close()

    type_counts = df_cleaned["type"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(type_counts.index, type_counts.values, color=['blue', 'orange'])
    ax.set_title("Distribution of Movies and TV Shows")
    ax.set_xlabel("Type")
    ax.set_ylabel("Count")
    plt.savefig(os.path.join(plots_folder, 'type_bar.png'))
    plt.close()

    top_countries = df_cleaned['country_grouped'].value_counts().head(5).index
    df_top = df_cleaned[df_cleaned['country_grouped'].isin(top_countries) & (df_cleaned['country_grouped'] != 'Others')]

    pivot = pd.pivot_table(df_top, index='country_grouped', columns='rating', values='title', aggfunc='count', fill_value=0)
    colors = ['blue','orange','green','red','purple','brown','pink','gray','indigo','cyan','magenta','turquoise','maroon']
    pivot.plot(kind='bar', figsize=(12, 8), width=0.5, color=colors[:pivot.shape[1]])
    plt.title("Ratings Distribution by Country")
    plt.xlabel("Country")
    plt.ylabel("Number of Titles")
    plt.xticks(rotation=0)
    plt.legend(title="Rating", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, 'rating_by_country.png'))
    plt.close()

    release_trend = df_cleaned['release_year'].value_counts().sort_index()
    plt.figure(figsize=(15, 8))
    plt.plot(release_trend.index, release_trend.values, color='#cfb8e6', linewidth=2, label='Total Titles')
    plt.scatter(release_trend.index, release_trend.values, marker="o", color='#9b6be8', s=30)
    plt.title("Netflix Movies Release Trend by Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Titles")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, 'release_trend.png'))
    plt.close()

    df_filtered = df_cleaned[df_cleaned['type'] == 'Movie']
    avg_duration = df_filtered.groupby(['release_year'])['duration_time'].mean().reset_index()
    avg_duration = avg_duration[avg_duration['release_year'] > 1940]

    plt.figure(figsize=(12, 6))
    plt.plot(avg_duration['release_year'], avg_duration['duration_time'], marker='o', color='blue')
    plt.title("Average Movie Duration Over Years")
    plt.xlabel("Release Year")
    plt.ylabel("Avg Duration (min)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_folder, 'avg_movie_duration.png'))
    plt.close()

    return render_template("plots.html")

if __name__ == '__main__':
    app.run(debug=True)
