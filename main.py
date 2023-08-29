import os
import configparser
from datetime import date
from urllib.parse import urlparse

import pandas as pd

from utils import Logger

CONFIG = configparser.ConfigParser()

with open("./settings/settings.ini", "r") as file:
    CONFIG.read_file(file)

INPUT_PATH = CONFIG.get("paths", "input")

OUTPUT_PATH = CONFIG.get("paths", "output")

class URLChecker:
    """Checks urls for duplicates and count the number of urls that share domain"""
    def __init__(self) -> None:
        self.logger = Logger(__class__.__name__)
        self.logger.info("*****URLChecker started*****")
        
        self.crawled: list[str] = []
        self.duplicates: list[str] = []
        self.non_duplicates: list[str] = []
        self.results: list[dict[str, str]] = []

    def __read_input_excel(self) -> list[str]:
        """Reads the input excel and outputs a list of urls found"""
        for file in os.listdir(INPUT_PATH):
            if not file.endswith("xlsx"):continue

            self.logger.info("Reading input file >>> {}".format(file))

            df = pd.read_excel(f"{INPUT_PATH}{file}")

            urls_dict: dict[str, dict] = df[["url", "canonicalUrl"]].to_dict()

            urls = []

            for _, value in urls_dict.items():
                values = list(value.values())

                for url in values:
                    if isinstance(url, str) and url.startswith("http"):
                        urls.append(url)
            
            return urls

        self.logger.error("Excel file not found in input path!!")

    def __remove_duplicates(self, urls: list[str]) -> None:
        """Removes duplicates from the list of urls"""
        for url in urls:
            if url in self.non_duplicates:
                self.duplicates.append("")
            else:
                self.non_duplicates.append(url)
        
        self.logger.info("Non duplicates: {} || Duplicates: {}".format(
                            len(self.non_duplicates),  len(self.duplicates)))

    def __count_urls_per_domain(self, domain: str) -> int:
        """Counts the number of urls in a given domain"""
        count = []

        for url in self.non_duplicates:
            if urlparse(url).netloc == domain:
                count.append("")
        
        return len(count)
    
    def __save_to_excel(self) -> None:
        """Saves results obtained to an excel file"""
        self.logger.info("Savig results obtained to excel...")
        df = pd.DataFrame(self.results).sort_values("Results Found", ascending=False)

        filename = f"results_{date.today()}.xlsx"

        df.to_excel(f"{OUTPUT_PATH}{filename}", index=False)

        self.logger.info("Data saved to {}".format(filename))

    def run(self) -> None:
        """Entry point to the URLChecker"""
        urls = self.__read_input_excel()

        self.__remove_duplicates(urls)

        for url in urls:
            if not url in self.crawled:
                domain = urlparse(url).netloc

                count = self.__count_urls_per_domain(domain)

                self.results.append({"URL": url, "Results Found": count})

                self.crawled.append(url)

        self.__save_to_excel()
    

if __name__ == "__main__":
    app = URLChecker()
    app.run()