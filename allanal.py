import os
import csv
import requests
import pandas as pd
from bs4 import BeautifulSoup


class AllAnalScraper:
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
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

    def scrape_website(self):
        page_number = 1

        while True:
            url = f'{self.base_url}/scenes?page={page_number}&order_by=publish_date&sort_by=desc'
            soup = self.get_soup(url)

            content_cards = soup.select('.content-border')
            if not content_cards:
                break

            for card in content_cards:
                title = card.select_one('.content-title').text.strip()
                duration_str = card.select_one('.total-time').text.strip()
                duration = self.parse_duration(duration_str)
                movie_data = {"Title": title, "Duration": duration, "Website": "AllAnal"}
                self.append_data_to_csv(self.file_paths['movies'], [movie_data], "Title")

                image_urls = [img['src'] for img in card.select('img[src]')]
                image_urls += [div['style'].split('url(')[1].split(')')[0] for div in card.select('.thumb-mouseover')]
                for image_url in image_urls:
                    image_data = {"Title": title, "URL": image_url}
                    self.append_data_to_csv(self.file_paths['images'], [image_data], ["Title", "URL"])

                models_elem = card.select_one('.content-models')
                if models_elem:
                    models_text = models_elem.get_text(strip=True)
                    if models_text.startswith("Models:"):
                        models_text = models_text[len("Models:"):].strip()
                        models = [model.strip() for model in models_text.split(',')]
                    for model in models:
                        star_data = {"Name": model}
                        self.append_data_to_csv(self.file_paths['stars'], [star_data], "Name")
                        movie_star_data = {"Title": title, "Name": model}
                        self.append_data_to_csv(self.file_paths['movie_stars'], [movie_star_data], ["Title", "Name"])

            page_number += 1
            print(page_number)


if __name__ == "__main__":
    scraper = AllAnalScraper('https://tour.allanal.com')
    scraper.scrape_website()