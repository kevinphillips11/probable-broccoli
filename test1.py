import pandas as pd
from collections import Counter

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('./data/movie_stars.csv')

# Count the occurrences of each star's name
star_counts = Counter(df['Name'])

# Get the top k stars (e.g., top 10)
k = 30
top_stars = star_counts.most_common(k)

# Print the top k stars and their counts
print(f'Top {k} stars:')
for star, count in top_stars:
    print(f'{star}: {count} movies')
