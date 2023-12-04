import os
import re
import csv
import requests
import pandas as pd
from bs4 import BeautifulSoup


class SwallowedScraper:
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
        
    def extract_model_names(self, model_string):
        model_names = re.sub(r'Models?:', '', model_string).strip()
        return [name.strip() for name in model_names.split(',') if name.strip() != ""]


    def scrape_website(self):
        page_number = 1

        while True:
            url = f'{self.base_url}/scenes?page={page_number}&order_by=publish_date&sort_by=desc'
            soup = self.get_soup(url)

            items = soup.select('.content-item')
            if not items:
                break

            for item in items:
                title = item.select_one('.content-title').text.strip()
                duration_str = item.select_one('.total-time').text.strip().split(' ')[0]
                duration = self.parse_duration(duration_str)
                movie_data = {"Title": title, "Duration": duration, "Website": "Swallowed"}
                self.append_data_to_csv(self.file_paths['movies'], [movie_data], "Title")

                img_urls = self.extract_image_urls(item)
                for image_url in img_urls:
                    image_data = {"Title": title, "URL": image_url}
                    self.append_data_to_csv(self.file_paths['images'], [image_data], ["Title", "URL"])

                models_text = item.select_one('.content-models').text
                models = self.extract_model_names(models_text)
                for model in models:
                    star_data = {"Name": model}
                    self.append_data_to_csv(self.file_paths['stars'], [star_data], "Name")
                    movie_star_data = {"Title": title, "Name": model}
                    self.append_data_to_csv(self.file_paths['movie_stars'], [movie_star_data], ["Title", "Name"])

            page_number += 1
            print(page_number)

    @staticmethod
    def extract_image_urls(item):
        img_urls = []

        main_img = item.select_one('.lg-thumb img')
        if main_img:
            img_urls.append(main_img['src'])
        for thumb in item.select('.sm-thumb img'):
            img_urls.append(thumb['src'])
        for bg in item.select('.thumb-mouseover'):
            if bg.get('style'):
                bg_url = re.search(r'url\((.*?)\)', bg['style']).group(1).replace(' ', '')
                img_urls.append(bg_url)

        # Remove the first image if it's a logo
        if img_urls and 'logo' in img_urls[0].lower():
            img_urls.pop(0)

        return img_urls


if __name__ == "__main__":
    scraper = SwallowedScraper('https://tour.swallowed.com')
    scraper.scrape_website()