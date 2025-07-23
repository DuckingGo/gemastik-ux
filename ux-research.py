import spacy
import time
import os
import requests
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from transformers import pipeline
from bs4 import BeautifulSoup

class UXResearch:
    def __init__(self, model_name='facebook/bart-large-cnn'):
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

        # Try to find specific content sections
        article = soup.find('section', class_='news-article')
        if article:
            text = article.get_text(strip=True)
        else:
            # Fallback to main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                text = main_content.get_text(strip=True)
            else:
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(strip=True)
        
        # Clean the text and return a reasonable length
        return text[:2000] if len(text) > 2000 else text

    def summarize_text(self, text):
        return self.summarizer(text, max_length=130, min_length=30, do_sample=False)

    def analyze_text(self, text):
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def run_research(self, url):
        """ 
        Perform UX research analysis on a given URL
        Args:
            url (str): The URL to analyze
        Returns:
            dict: Contains summary, analysis results, and word cloud path
        """
        start_time = time.time()
        print(f"\n=== Starting UX Research Analysis for: {url} ===")
        
        html_content = self.fetch_web_content(url)
        if not html_content:
            print("Failed to fetch content. Skipping this URL.")
            return None
        
        text_content = self.parse_html(html_content)
        if not text_content or len(text_content.strip()) < 50:
            print("Insufficient content extracted. Skipping analysis.")
            return None
            
        print(f"Extracted {len(text_content)} characters of content.")
        
        # Generate summary
        try:
            summary = self.summarize_text(text_content)
            summary_text = summary[0]['summary_text'] if summary else "Summary not available"
        except Exception as e:
            print(f"Error generating summary: {e}")
            summary_text = "Summary generation failed"
        
        # Perform enhanced analysis
        analysis = self.enhanced_analysis(text_content)
        
        # Generate word cloud
        timestamp = int(time.time())
        wordcloud_path = f"wordcloud_{timestamp}.png"
        domain = url.split('/')[2] if '//' in url else 'unknown'
        wordcloud_title = f"SDG UX Research - {domain}"
        
        wordcloud = self.generate_wordcloud(text_content, wordcloud_title, wordcloud_path)
        
        end_time = time.time()
        
        # Display results
        print(f"\n--- ANALYSIS RESULTS ---")
        print(f"Summary: {summary_text}")
        print(f"Entities found: {len(analysis['entities'])}")
        print(f"Top keywords: {[kw[0] for kw in analysis['top_keywords'][:5]]}")
        print(f"Sentences: {analysis['sentence_count']}, Tokens: {analysis['token_count']}")
        print(f"Research completed in {end_time - start_time:.2f} seconds.")
        
        return {
            'url': url,
            'summary': summary_text,
            'analysis': analysis,
            'wordcloud_path': wordcloud_path,
            'processing_time': end_time - start_time
        }

    def save_results(self, results):
        """
        Save comprehensive research results to file
        Args:
            results (dict): The results dictionary containing analysis data
        Returns:
            str: Path to the saved results file, or None if saving failed
        """
        if not results:
            return None
            
        timestamp = int(time.time())
        filename = f"sdg_ux_research_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write("=" * 60 + "\n")
                file.write("SDG UX RESEARCH ANALYSIS REPORT\n")
                file.write("=" * 60 + "\n\n")
                
                file.write(f"URL: {results['url']}\n")
                file.write(f"Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write(f"Processing Time: {results['processing_time']:.2f} seconds\n\n")
                
                file.write("SUMMARY:\n")
                file.write("-" * 20 + "\n")
                file.write(f"{results['summary']}\n\n")
                
                file.write("KEY INSIGHTS:\n")
                file.write("-" * 20 + "\n")
                analysis = results['analysis']
                file.write(f"Total Sentences: {analysis['sentence_count']}\n")
                file.write(f"Total Tokens: {analysis['token_count']}\n")
                file.write(f"Average Sentence Length: {analysis['avg_sentence_length']:.1f} words\n\n")
                
                file.write("TOP KEYWORDS:\n")
                for i, (keyword, freq) in enumerate(analysis['top_keywords'][:10], 1):
                    file.write(f"{i}. {keyword} (frequency: {freq})\n")
                file.write("\n")
                
                file.write("NAMED ENTITIES:\n")
                for entity, label in analysis['entities'][:15]:
                    file.write(f"- {entity} ({label})\n")
                file.write("\n")
                
                file.write("SAMPLE CONTENT:\n")
                file.write("-" * 20 + "\n")
                for i, sentence in enumerate(analysis['sample_sentences'], 1):
                    file.write(f"{i}. {sentence[:200]}...\n")
                
                file.write(f"\nWord Cloud saved as: {results['wordcloud_path']}\n")
                
            print(f"Comprehensive results saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving results: {e}")
            return None

    def generate_wordcloud(self, text, title="Word Cloud", save_path=None):
        """
        Generate and display a word cloud from text content
        Args:
            text (str): The text to generate the word cloud from
            title (str): Title for the word cloud plot
            save_path (str): Path to save the word cloud image
        Returns:
            WordCloud: Generated word cloud object
        """
        try:
            # Create word cloud
            wordcloud = WordCloud(
                width=1200, 
                height=600, 
                background_color='white',
                max_words=100,
                relative_scaling=0.5,
                colormap='viridis'
            ).generate(text)
            
            # Create plot
            plt.figure(figsize=(15, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=16, fontweight='bold')
            plt.tight_layout(pad=0)
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"Word cloud saved to: {save_path}")
            
            plt.show()
            return wordcloud
        except Exception as e:
            print(f"Error generating word cloud: {e}")
            return None

    def extract_keywords(self, text, num_keywords=10):
        """
        Extract key entities and important terms from text
        Args:
            text (str): The text to analyze
            num_keywords (int): Number of top keywords to return
        Returns:
            dict: Contains entities, keywords, and their frequency
        """
        doc = self.nlp(text)
        
        # Extract entities
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Extract important tokens (nouns, adjectives, proper nouns)
        keywords = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        # Count frequency and get top keywords
        from collections import Counter
        keyword_freq = Counter(keywords)
        top_keywords = keyword_freq.most_common(num_keywords)
        
        return {
            'entities': entities,
            'keywords': top_keywords,
            'keyword_freq': keyword_freq
        }

    def enhanced_analysis(self, text):
        """
        Perform comprehensive text analysis including sentiment and readability
        Args:
            text (str): The text to analyze
        Returns:
            dict: Analysis results including tokens, sentences, entities, and keywords
        """
        doc = self.nlp(text)
        
        # Basic linguistic analysis
        tokens = [(token.text, token.pos_, token.dep_) for token in doc]
        sentences = [sent.text for sent in doc.sents]
        
        # Extract keywords and entities
        keyword_analysis = self.extract_keywords(text)
        
        # Calculate basic readability metrics
        avg_sentence_length = len(doc) / len(sentences) if sentences else 0
        
        return {
            'tokens': tokens[:20],  # Limit for readability
            'sentence_count': len(sentences),
            'token_count': len(doc),
            'avg_sentence_length': avg_sentence_length,
            'entities': keyword_analysis['entities'],
            'top_keywords': keyword_analysis['keywords'],
            'sample_sentences': sentences[:3]  # First 3 sentences
        }

if __name__ == "__main__":
    urls = [
        "https://sdgs.un.org/news/governments-must-seek-win-win-synergies-tackling-climate-and-sustainable-development-crises",
        "https://sdgs.un.org/blog/expert-group-prepare-report-analysing-climate-and-sdg-synergies-aiming-maximize-action-impact",
        "https://sdgs.un.org/news/call-inputs-global-sustainable-development-report-2023-34347"
    ]
    
    print("SDG UX Research Analytics")
    print("=" * 60)
    
    if not all(url.startswith('http') for url in urls):
        print("Error: Please ensure all URLs are valid HTTP/HTTPS links.")
    else:
        research = UXResearch()
        all_results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\nProcessing URL {i}/{len(urls)}")
            results = research.run_research(url)
            
            if results:
                # Save individual results
                filename = research.save_results(results)
                all_results.append(results)
                print(f"Analysis completed for URL {i}")
            else:
                print(f"Failed to analyze URL {i}")
        
        print(f"\nUX Research Analysis Complete!")
        print(f"Successfully analyzed {len(all_results)} out of {len(urls)} URLs")
        print(f"Results and word clouds saved to current directory")
        
        if all_results:
            # Generate summary statistics
            total_entities = sum(len(r['analysis']['entities']) for r in all_results)
            total_keywords = sum(len(r['analysis']['top_keywords']) for r in all_results)
            avg_processing_time = sum(r['processing_time'] for r in all_results) / len(all_results)
            
            print(f"\nSUMMARY STATISTICS:")
            print(f" - Total Entities Extracted: {total_entities}")
            print(f" - Total Keywords Identified: {total_keywords}")
            print(f" - Average Processing Time: {avg_processing_time:.2f} seconds")
            print(f" - Word Clouds Generated: {len(all_results)}")
            
        print("\nEnterprise UX Research Analysis completed successfully!")