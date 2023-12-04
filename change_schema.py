import os
import pandas as pd

# Define the paths to the original CSV files and the destination folder
data_folder = './data'
destination_folder = './data1'

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Read the original CSV files
movies_df = pd.read_csv(os.path.join(data_folder, 'movies.csv'))
stars_df = pd.read_csv(os.path.join(data_folder, 'stars.csv'))
movie_stars_df = pd.read_csv(os.path.join(data_folder, 'movie_stars.csv'))
images_df = pd.read_csv(os.path.join(data_folder, 'images.csv'))
star_images_df = pd.read_csv(os.path.join(data_folder, 'model-images.csv'))

# Create the new tables based on the schema

# Create the Images Table
images_table = images_df.rename(columns={'URL': 'ImageURL'})

# Create the StarImages Table
star_images_table = star_images_df.rename(columns={'Model Name': 'Name', 'Image_URL': 'URL'})

# Create the Stars Table
stars_table = stars_df.merge(star_images_table[['Model Name', 'ImageURL']], on='Model Name', how='left').drop_duplicates()

# Create the Movies Table
movies_table = movies_df.merge(images_table[['Title', 'ImageURL']], on='Title', how='left')

# Create the MovieStars Table
movie_stars_table = movie_stars_df.merge(movies_table[['Title', 'MovieID']], on='Title', how='left')
movie_stars_table = movie_stars_table.merge(stars_table[['Model Name', 'StarID']], on='Model Name', how='left')

# Save the new tables as CSV files in the destination folder
movies_table.to_csv(os.path.join(destination_folder, 'movies.csv'), index=False)
stars_table.to_csv(os.path.join(destination_folder, 'stars.csv'), index=False)
movie_stars_table.to_csv(os.path.join(destination_folder, 'movie_stars.csv'), index=False)
images_table.to_csv(os.path.join(destination_folder, 'images.csv'), index=False)
star_images_table.to_csv(os.path.join(destination_folder, 'star-images.csv'), index=False)
