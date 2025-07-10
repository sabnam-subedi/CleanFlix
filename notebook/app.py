from flask import Flask, render_template, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# Load cleaned data globally once
base_dir = os.path.dirname(os.path.abspath(__file__))
cleaned_path = os.path.join(base_dir, '..', 'data', 'cleaned', 'netflix_cleaned.xlsx')
df_cleaned = pd.read_excel(cleaned_path)
columns = df_cleaned.columns.tolist()

@app.route('/')
def home()
    return render_template("index.html")

@app.route('/data')
def show_cleaned_data():
    return render_template("data.html", columns=columns)

@app.route('/api/data')
def api_data():
    try:
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
    except Exception as e:
        print("❌ ERROR LOADING FILE:", e)
        return f"<h1>Error loading data</h1><p>{e}</p>", 500

@app.route('/raw')
def show_raw_data():
    try:
        raw_path = os.path.join(base_dir, '..', 'data', 'raw', 'netflix_titles.csv')
        print("📂 Reading raw data from:", raw_path)

        df_raw = pd.read_csv(raw_path)
        table = df_raw.to_html(classes="display", index=False)

        return render_template('raw.html', table=table)
    except Exception as e:
        print("❌ ERROR LOADING RAW FILE:", e)
        return f"<h1>Error loading raw data</h1><p>{e}</p>", 500

if __name__ == '__main__':
    app.run(debug=True)
