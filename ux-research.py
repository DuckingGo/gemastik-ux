import spacy
import time
import os
import requests

from transformers import pipeline
from bs4 import BeautifulSoup

class UXResearch:
    def __init__(self, model_name='distilbert-base-uncased'):
        self.nlp = spacy.load("en_core_web_sm")
        self.summarizer = pipeline("summarization", model=model_name)

    def fetch_web_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    def summarize_text(self, text):
        return self.summarizer(text, max_length=130, min_length=30, do_sample=False)

    def analyze_text(self, text):
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def run_research(self, url):
        start_time = time.time()
        html_content = self.fetch_web_content(url)
        
        if not html_content:
            return
        
        text_content = self.parse_html(html_content)
        summary = self.summarize_text(text_content)
        analysis = self.analyze_text(text_content)

        end_time = time.time()
        
        print(f"Summary: {summary[0]['summary_text']}")
        print(f"Text Analysis: {analysis}")
        print(f"Research completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    url = input("Enter the URL for UX research: ")
    if not url.startswith('http'):
        print("Please enter a valid URL.")
    else:
        research = UXResearch()
        research.run_research(url)
        print("UX research completed successfully.")
        if os.path.exists('ux-research.py'):
            print("Script executed successfully.")
        else:
            print("Script file not found.")
    