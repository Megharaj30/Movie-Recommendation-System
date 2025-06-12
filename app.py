from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer  # Changed here
from difflib import get_close_matches

app = Flask(__name__)
df = pd.read_csv('new.csv')

# Fill NaN with empty strings
df.fillna('', inplace=True)

# Combine features for vectorization
def create_soup(x):
    return f"{x['title']} {x['genres']} {x['cast']} {x['director']}"

df['soup'] = df.apply(create_soup, axis=1)

# Vectorize and compute similarity matrix using TF-IDF
vectorizer = TfidfVectorizer(stop_words='english')  # Changed here
vector_matrix = vectorizer.fit_transform(df['soup'])
similarity = cosine_similarity(vector_matrix, vector_matrix)

# Store recent searches
recent_searches = []

@app.route('/')
def index():
    trending = df.sort_values(by='popularity', ascending=False).head(8)
    return render_template('index.html', trending=trending.to_dict(orient='records'), recent=recent_searches)

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_name = request.form['movie_name']
    movie_name_lower = movie_name.lower()

    titles = df['title'].tolist()
    match = get_close_matches(movie_name, titles, n=1, cutoff=0.6)

    if not match:
        return render_template('results.html', error="Movie not found 😢")

    index = df[df['title'] == match[0]].index[0]

    sim_scores = list(enumerate(similarity[index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:21]
    movie_indices = [i[0] for i in sim_scores]

    selected = df.iloc[index]
    recommended = df.iloc[movie_indices]

    movie_info = {
        'title': selected['title'],
        'director': selected['director'],
        'cast': selected['cast'],
        'runtime': selected['runtime'],
        'rating': selected['vote_average'],
        'trailer_url': selected['trailer_url']
    }

    rec_movies = []
    for _, row in recommended.iterrows():
        rec_movies.append({
            'title': row['title'],
            'director': row['director'],
            'runtime': row['runtime'],
            'rating': row['vote_average'],
            'trailer_url': row['trailer_url']
        })

    if selected['title'] not in recent_searches:
        recent_searches.insert(0, selected['title'])
        if len(recent_searches) > 5:
            recent_searches.pop()

    return render_template('results.html', movie=movie_info, recommended=rec_movies)

@app.route('/genre/<genre_name>')
def genre_filter(genre_name):
    genre_movies = df[df['genres'].str.contains(genre_name, case=False, na=False)]
    return render_template('results.html', movie={'title': f'{genre_name} Movies'}, recommended=genre_movies.head(10).to_dict(orient='records'))

@app.route('/suggest')
def suggest():
    query = request.args.get('q', '').lower()
    suggestions = df[df['title'].str.lower().str.startswith(query)]['title'].head(5).tolist()
    return jsonify({'suggestions': suggestions})

@app.route('/clear')
def clear_recent():
    recent_searches.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
