import os
import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd

class AnalOnlyScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data_dir = './data/'
        self.initialize_directories()
        self.initialize_csv_files()

    def initialize_directories(self):
        os.makedirs(self.data_dir, exist_ok=True)

    def initialize_csv_files(self):
        self.file_paths = {
            "movies": os.path.join(self.data_dir, 'movies.csv'),
            "images": os.path.join(self.data_dir, 'images.csv'),
            "stars": os.path.join(self.data_dir, 'stars.csv'),
            "movie_stars": os.path.join(self.data_dir, 'movie_stars.csv')
        }

        self.headers = {
            "movies": ['Title', 'Duration', 'Website'],
            "images": ['Title', 'URL'],
            "stars": ['Name'],
            "movie_stars": ['Title', 'Name']
        }

        for file, headers in self.headers.items():
            self.ensure_csv_header(self.file_paths[file], headers)

    @staticmethod
    def get_soup(url):
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    @staticmethod
    def ensure_csv_header(file, headers):
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            with open(file, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(headers)

    def append_data_to_csv(self, file, data, primary_key):
        if not os.path.exists(file):
            data_df = pd.DataFrame(data)
        else:
            existing_df = pd.read_csv(file)
            data_df = pd.DataFrame(data)
            combined_df = pd.concat([existing_df, data_df])
            
            # Check if primary_key is a string or a list. If string, convert to list
            primary_key = primary_key if isinstance(primary_key, list) else [primary_key]
            
            combined_df.drop_duplicates(subset=primary_key, inplace=True, keep="last")
            data_df = combined_df

        data_df.to_csv(file, index=False, encoding='utf-8')

    def scrape_website(self):
        page_number = 1
        while True:
            url_path_query = f'/scenes?page={page_number}&order_by=publish_date&sort_by=desc'
            url = self.base_url + url_path_query
            soup = self.get_soup(url)

            scene_divs = soup.find_all('div', class_='content-border')
            if not scene_divs:
                break

            for div in scene_divs:
                title = div.find('a', class_='content-title').text.strip()
                duration_str = div.find('span', class_='total-time').text.strip()
                duration = self.parse_duration(duration_str)
                models = [name.strip() for name in div.find('h4', class_='content-models').text.split(': ')[1].split(',')]

                movie_data = {"Title": title, "Duration": duration, "Website": "AnalOnly"}
                self.append_data_to_csv(self.file_paths['movies'], [movie_data], "Title")

                img_urls = [img['src'] for img in div.find_all('img')]
                bg_imgs = [div['style'].split('url(')[1].split(')')[0] for div in div.find_all('div', class_='thumb-mouseover')]
                img_urls.extend(bg_imgs)
                for img_url in img_urls:
                    image_data = {"Title": title, "URL": img_url}
                    self.append_data_to_csv(self.file_paths['images'], [image_data], ["Title", "URL"])

                for model in models:
                    star_data = {"Name": model}
                    self.append_data_to_csv(self.file_paths['stars'], [star_data], "Name")
                    movie_star_data = {"Title": title, "Name": model}
                    self.append_data_to_csv(self.file_paths['movie_stars'], [movie_star_data], ["Title", "Name"])

            page_number += 1
            print(page_number)

    def parse_duration(self, duration_str):
        time_parts = list(map(int, duration_str.split(':')))
        if len(time_parts) == 3:
            hours, minutes, seconds = time_parts
            return hours * 60 + minutes + (seconds // 60)
        elif len(time_parts) == 2:
            minutes, seconds = time_parts
            return minutes + (seconds // 60)
        else:
            raise ValueError("Unexpected duration format")

if __name__ == "__main__":
    scraper = AnalOnlyScraper('https://tour.analonly.com')
    scraper.scrape_website()