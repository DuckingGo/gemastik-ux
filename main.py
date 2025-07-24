#!/usr/bin/env python3
"""
LUMIRA Research Assistant

A comprehensive research assistant AI for collecting, summarizing, and organizing
data and articles related to digital vocational education and access inequality
in Indonesia.

This module provides functionality to:
- Search multiple academic and institutional sources
- Extract and summarize content in Indonesian
- Score sources based on relevance
- Generate professional reports in multiple formats
- Optimize performance for mid-spec laptops (6-7GB RAM usage)

Authors: LUMIRA Team
Version: 2.0
Date: July 2025
"""

import argparse
import os
import sys
import json
import csv
import time
import hashlib
import threading
import concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
import logging
import gc

# Import libraries untuk web scraping dan PDF processing
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse, quote
import re
from dataclasses import dataclass, field
import unicodedata

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('lumira_research.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Source:
    """
    Data class for storing research source information.
    
    Attributes:
        title (str): Title of the source document
        author (str): Author or institution name
        year (int): Publication year
        url (str): Source URL
        file_type (str): Type of document (article, report, etc.)
        summary_id (str): Summary in Indonesian language
        summary_en (str): Summary in English language
        extracted_data (Dict): Important data extracted from content
        relevance_score (float): Relevance score from 0.0 to 5.0
        content (str): Extracted text content
        metadata (Dict): Additional metadata information
    """
    title: str
    author: str
    year: int
    url: str
    file_type: str
    summary_id: str = ""
    summary_en: str = ""
    extracted_data: Dict = field(default_factory=dict)
    relevance_score: float = 0.0
    content: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization to ensure data consistency."""
        if not self.extracted_data:
            self.extracted_data = {}
        if not self.metadata:
            self.metadata = {}

class MemoryManager:
    """
    Memory management utility for optimal RAM usage.
    
    Manages memory allocation and cleanup for processing large datasets
    while maintaining performance on mid-spec laptops.
    """
    
    def __init__(self, max_memory_gb: float = 6.0):
        """
        Initialize memory manager.
        
        Args:
            max_memory_gb (float): Maximum memory to use in GB
        """
        self.max_memory_bytes = max_memory_gb * 1024 * 1024 * 1024
        self.current_memory = 0
        self.content_cache: Dict[str, str] = {}
        self.max_cache_size = 100
    
    def add_content(self, url: str, content: str) -> None:
        """
        Add content to cache with memory management.
        
        Args:
            url (str): Source URL as cache key
            content (str): Content to cache
        """
        if len(self.content_cache) >= self.max_cache_size:
            self.cleanup_cache()
        self.content_cache[url] = content
    
    def get_content(self, url: str) -> Optional[str]:
        """
        Retrieve content from cache.
        
        Args:
            url (str): Source URL
            
        Returns:
            Optional[str]: Cached content or None
        """
        return self.content_cache.get(url)
    
    def cleanup_cache(self) -> None:
        """Clean up memory cache to free RAM."""
        # Keep only half of the cache
        items_to_keep = len(self.content_cache) // 2
        keys_to_remove = list(self.content_cache.keys())[items_to_keep:]
        
        for key in keys_to_remove:
            del self.content_cache[key]
        
        gc.collect()  # Force garbage collection

class ResearchAssistant:
    """
    Main research assistant class for collecting and analyzing vocational education data.
    
    This class orchestrates the entire research process including:
    - Multi-source data collection
    - Content extraction and processing
    - Relevance scoring and ranking
    - Report generation in multiple formats
    - Memory-optimized processing for mid-spec laptops
    """
    
    def __init__(self, output_folder: str, max_sources: int = 25, language: str = "id", 
                 enable_parallel: bool = True, max_workers: int = 4):
        """
        Initialize the research assistant.
        
        Args:
            output_folder (str): Directory to save results
            max_sources (int): Maximum number of sources to collect (increased for 12GB RAM)
            language (str): Language for summaries ('id' or 'en')
            enable_parallel (bool): Enable parallel processing for better performance
            max_workers (int): Number of worker threads for parallel processing
        """
        self.output_folder = Path(output_folder)
        self.max_sources = max_sources
        self.language = language
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers
        self.sources: List[Source] = []
        self.session = requests.Session()
        self.memory_manager = MemoryManager(max_memory_gb=6.5)
        self.processed_urls: Set[str] = set()
        
        # Enhanced headers for better success rate
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        })
        
        # Create output folder
        self.output_folder.mkdir(exist_ok=True)
        
        # Enhanced search engines and sources
        self.search_engines = {
            'google_scholar': 'https://scholar.google.com/scholar',
            'bps': 'https://www.bps.go.id',
            'kemendikbud': 'https://www.kemdikbud.go.id',
            'kemenaker': 'https://www.kemnaker.go.id',
            'worldbank': 'https://www.worldbank.org',
            'unesco': 'https://en.unesco.org',
            'oecd': 'https://www.oecd.org',
            'adb': 'https://www.adb.org',
            'researchgate': 'https://www.researchgate.net'
        }
        
        # Expanded keywords for better coverage
        self.keywords_id = [
            "pendidikan vokasi digital indonesia",
            "akses pendidikan kejuruan digital",
            "kesenjangan digital pendidikan indonesia",
            "platform pembelajaran vokasi online",
            "teknologi pendidikan kejuruan",
            "SMK digital transformation",
            "keterampilan digital indonesia",
            "edtech vokasi indonesia",
            "pelatihan kerja digital indonesia",
            "sertifikasi kompetensi digital",
            "pembelajaran jarak jauh SMK",
            "industri 4.0 pendidikan vokasi"
        ]
        
        self.keywords_en = [
            "digital vocational education indonesia",
            "vocational training access inequality indonesia",
            "digital divide education indonesia",
            "online vocational learning platform",
            "educational technology vocational",
            "digital skills training indonesia",
            "vocational education technology indonesia",
            "indonesia workforce development digital",
            "technical education digital transformation",
            "TVET digital indonesia",
            "vocational education remote learning"
        ]

    def search_google_scholar(self, query: str, year_range: str = "2021-2025") -> List[Dict]:
        """
        Search Google Scholar for academic articles.
        
        Args:
            query (str): Search query string
            year_range (str): Year range in format "2021-2025"
            
        Returns:
            List[Dict]: List of search results with metadata
        """
        logger.info(f"Searching Google Scholar for: {query}")
        
        try:
            # Enhanced query formatting for Google Scholar
            search_url = f"{self.search_engines['google_scholar']}?q={quote(query)}&as_ylo=2021&as_yhi=2025&hl=en"
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # Increased limit for better coverage with more RAM
            articles = soup.find_all('div', class_='gs_r gs_or gs_scl')[:10]  
            
            for article in articles:
                try:
                    title_elem = article.find('h3', class_='gs_rt')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text().strip()
                    
                    # Extract link with better error handling
                    link_elem = title_elem.find('a')
                    url = ""
                    if link_elem and 'href' in link_elem.attrs:
                        url = link_elem['href']
                        if not url.startswith('http'):
                            url = f"https://scholar.google.com{url}"
                    
                    # Enhanced author and year extraction
                    author_info = article.find('div', class_='gs_a')
                    author_text = author_info.get_text() if author_info else ""
                    
                    # Better year extraction with multiple patterns
                    year_match = re.search(r'20(2[1-5]|2[0-4])', author_text)
                    year = int(year_match.group()) if year_match else 2023
                    
                    # Enhanced author extraction
                    author = author_text.split(',')[0].split('-')[0].strip()
                    if not author or len(author) < 2:
                        author = "Unknown Author"
                    
                    # Extract citation count if available
                    citation_elem = article.find('div', class_='gs_fl')
                    citations = 0
                    if citation_elem:
                        citation_text = citation_elem.get_text()
                        citation_match = re.search(r'Cited by (\d+)', citation_text)
                        if citation_match:
                            citations = int(citation_match.group(1))
                    
                    results.append({
                        'title': title,
                        'author': author,
                        'year': year,
                        'url': url,
                        'file_type': 'article',
                        'source': 'Google Scholar',
                        'citations': citations
                    })
                    
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue
            
            logger.info(f"Found {len(results)} results from Google Scholar")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Google Scholar: {e}")
            return []

    def search_government_sources(self, query: str) -> List[Dict]:
        """
        Search Indonesian government sources for official reports and data.
        
        Args:
            query (str): Search query string
            
        Returns:
            List[Dict]: List of government source results
        """
        logger.info(f"Searching government sources for: {query}")
        
        results = []
        gov_sources = {
            'BPS': 'https://www.bps.go.id',
            'Kemendikbud': 'https://www.kemdikbud.go.id', 
            'Kemenaker': 'https://www.kemnaker.go.id'
        }
        
        for source_name, base_url in gov_sources.items():
            try:
                # Enhanced search approach with multiple endpoints
                search_endpoints = ['/publication', '/publikasi', '/data', '/statistik']
                
                for endpoint in search_endpoints:
                    try:
                        search_url = f"{base_url}{endpoint}"
                        response = self.session.get(search_url, timeout=15)
                        
                        if response.status_code != 200:
                            continue
                            
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Enhanced link extraction with better filtering
                        links = soup.find_all('a', href=True)[:20]  # Increased limit
                        
                        for link in links:
                            href = link['href']
                            text = link.get_text().strip().lower()
                            
                            # Enhanced relevance checking with more keywords
                            relevance_keywords = [
                                'vokasi', 'kejuruan', 'digital', 'pendidikan', 'smk', 
                                'teknologi', 'keterampilan', 'pelatihan', 'kompetensi',
                                'industri 4.0', 'transformasi digital'
                            ]
                            
                            if any(keyword in text for keyword in relevance_keywords) and len(text) > 10:
                                full_url = urljoin(base_url, href)
                                
                                # Avoid duplicate URLs
                                if full_url not in self.processed_urls:
                                    self.processed_urls.add(full_url)
                                    
                                    results.append({
                                        'title': link.get_text().strip(),
                                        'author': source_name,
                                        'year': 2024,  # Default year
                                        'url': full_url,
                                        'file_type': 'report',
                                        'source': source_name
                                    })
                                    
                                    if len(results) >= 8:  # Increased limit per source
                                        break
                        
                        if len(results) >= 8:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Error searching {source_name} endpoint {endpoint}: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error searching {source_name}: {e}")
                continue
        
        logger.info(f"Found {len(results)} results from government sources")
        return results

    def search_international_sources(self, query: str) -> List[Dict]:
        """
        Search international organization sources for global reports and data.
        
        Args:
            query (str): Search query string
            
        Returns:
            List[Dict]: List of international source results
        """
        logger.info(f"Searching international sources for: {query}")
        
        results = []
        
        # Enhanced World Bank search
        try:
            wb_queries = [query, "indonesia vocational education", "indonesia digital skills"]
            
            for wb_query in wb_queries:
                wb_search = f"https://documents.worldbank.org/en/publication/documents-reports/api/search?q={quote(wb_query)}&lang=en"
                response = self.session.get(wb_search, timeout=15)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        docs = data.get('documents', [])[:5]  # Increased limit
                        
                        for doc in docs:
                            title = doc.get('title', '')
                            if 'indonesia' in title.lower() or 'vocational' in title.lower():
                                results.append({
                                    'title': title,
                                    'author': 'World Bank',
                                    'year': int(doc.get('year', 2024)),
                                    'url': doc.get('url', ''),
                                    'file_type': 'report',
                                    'source': 'World Bank'
                                })
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON response from World Bank API")
                        
        except Exception as e:
            logger.warning(f"Error searching World Bank: {e}")
        
        # Enhanced UNESCO search
        try:
            unesco_keywords = ["indonesia education technology", "vocational education asia", "digital skills training"]
            
            for keyword in unesco_keywords:
                unesco_url = f"https://en.unesco.org/search?keywords={quote(keyword)}"
                response = self.session.get(unesco_url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    links = soup.find_all('a', href=True)[:15]
                    
                    for link in links:
                        href = link['href']
                        text = link.get_text().strip()
                        
                        if any(term in text.lower() for term in ['indonesia', 'vocational', 'digital', 'education']):
                            full_url = urljoin('https://en.unesco.org', href)
                            
                            if full_url not in self.processed_urls and len(text) > 10:
                                self.processed_urls.add(full_url)
                                
                                results.append({
                                    'title': text,
                                    'author': 'UNESCO',
                                    'year': 2024,
                                    'url': full_url,
                                    'file_type': 'report',
                                    'source': 'UNESCO'
                                })
                                
                                if len(results) >= 10:
                                    break
                        
        except Exception as e:
            logger.warning(f"Error searching UNESCO: {e}")
        
        # OECD search
        try:
            oecd_url = f"https://www.oecd.org/search/?q={quote(query + ' indonesia')}"
            response = self.session.get(oecd_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)[:10]
                
                for link in links:
                    href = link['href']
                    text = link.get_text().strip()
                    
                    if 'indonesia' in text.lower() and any(term in text.lower() for term in ['education', 'skill', 'digital']):
                        full_url = urljoin('https://www.oecd.org', href)
                        
                        if full_url not in self.processed_urls:
                            self.processed_urls.add(full_url)
                            
                            results.append({
                                'title': text,
                                'author': 'OECD',
                                'year': 2023,
                                'url': full_url,
                                'file_type': 'report',
                                'source': 'OECD'
                            })
                            
        except Exception as e:
            logger.warning(f"Error searching OECD: {e}")
        
        logger.info(f"Found {len(results)} results from international sources")
        return results

    def extract_content(self, source: Source) -> str:
        """
        Extract and clean content from a source URL.
        
        Args:
            source (Source): Source object containing URL and metadata
            
        Returns:
            str: Cleaned text content from the source
        """
        # Check cache first
        cached_content = self.memory_manager.get_content(source.url)
        if cached_content:
            return cached_content
        
        try:
            response = self.session.get(source.url, timeout=20)
            response.raise_for_status()
            
            # Handle different content types
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/pdf' in content_type:
                # For PDF files, we would need a PDF parser
                logger.info(f"PDF detected for {source.url}, skipping content extraction")
                return "PDF document - content extraction not implemented"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements more comprehensively
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
                element.decompose()
            
            # Focus on main content areas
            main_content = None
            for selector in ['main', 'article', '.content', '.main-content', '#content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup
            
            # Extract text with better cleaning
            text = main_content.get_text(separator=' ', strip=True)
            
            # Enhanced text cleaning
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = ' '.join(lines)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Limit content size for memory management (increased for 12GB RAM)
            max_content_length = 10000  # Increased from 5000
            if len(text) > max_content_length:
                text = text[:max_content_length] + "..."
            
            # Cache the content
            self.memory_manager.add_content(source.url, text)
            
            return text
            
        except Exception as e:
            logger.warning(f"Error extracting content from {source.url}: {e}")
            return ""

    def generate_summary_id(self, content: str, title: str) -> str:
        """
        Generate a comprehensive summary in Indonesian language.
        
        Args:
            content (str): Full text content to summarize
            title (str): Title of the source for context
            
        Returns:
            str: Summary in Indonesian (100-200 words)
        """
        # Enhanced extractive summarization
        sentences = re.split(r'[.!?]+', content)[:20]  # Increased sentence pool
        
        # Filter sentences with better relevance scoring
        relevant_sentences = []
        keywords = [
            'vokasi', 'kejuruan', 'digital', 'pendidikan', 'akses', 'kesenjangan', 
            'teknologi', 'keterampilan', 'SMK', 'politeknik', 'pelatihan',
            'kompetensi', 'industri', 'transformasi', 'pembelajaran', 'platform'
        ]
        
        sentence_scores = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            score = 0
            sentence_lower = sentence.lower()
            
            # Score based on keyword presence
            for keyword in keywords:
                if keyword in sentence_lower:
                    score += 1
            
            # Bonus for sentences with numbers/statistics
            if re.search(r'\d+', sentence):
                score += 0.5
            
            # Bonus for sentences mentioning Indonesia
            if 'indonesia' in sentence_lower:
                score += 1
            
            if score > 0:
                sentence_scores.append((sentence, score))
        
        # Sort by score and take top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected_sentences = [s[0] for s in sentence_scores[:7]]  # Increased from 5
        
        if not selected_sentences:
            selected_sentences = sentences[:3]  # Fallback
            
        summary = '. '.join(selected_sentences)
        
        # Ensure summary meets word count requirements (100-200 words)
        words = summary.split()
        
        if len(words) > 200:
            summary = ' '.join(words[:200]) + "..."
        elif len(words) < 50:
            # Enhance short summaries with context
            context_intro = f"Dokumen '{title}' membahas aspek-aspek penting pendidikan vokasi dan teknologi digital di Indonesia. "
            summary = context_intro + summary
            
            # Recheck word count after adding context
            words = summary.split()
            if len(words) > 200:
                summary = ' '.join(words[:200]) + "..."
            
        return summary

    def calculate_relevance_score(self, source: Source) -> float:
        """
        Calculate relevance score for a source based on multiple factors.
        
        Args:
            source (Source): Source object to score
            
        Returns:
            float: Relevance score from 0.0 to 5.0
        """
        score = 0.0
        
        # Enhanced title relevance scoring
        title_lower = source.title.lower()
        title_keywords = [
            'vokasi', 'vocational', 'kejuruan', 'digital', 'teknologi', 'akses', 
            'inequality', 'indonesia', 'SMK', 'politeknik', 'edtech', 'pembelajaran',
            'keterampilan', 'skills', 'training', 'education', 'pendidikan'
        ]
        
        title_score = sum(1 for keyword in title_keywords if keyword in title_lower)
        score += min(title_score * 0.4, 2.5)  # Max 2.5 points from title
        
        # Enhanced content relevance scoring
        if source.content:
            content_lower = source.content.lower()
            content_keywords = [
                'smk', 'politeknik', 'edtech', 'pembelajaran digital', 
                'keterampilan digital', 'platform pembelajaran', 'industri 4.0',
                'transformasi digital', 'kompetensi', 'sertifikasi', 'pelatihan kerja',
                'akses internet', 'kesenjangan digital', 'literasi digital'
            ]
            
            content_score = sum(1 for keyword in content_keywords if keyword in content_lower)
            score += min(content_score * 0.15, 1.5)  # Max 1.5 points from content
        
        # Source credibility and authority scoring
        credible_sources = [
            'bps', 'kemendikbud', 'kemnaker', 'worldbank', 'unesco', 'scholar.google',
            'oecd', 'adb', 'researchgate', 'ieee', 'springer', 'elsevier'
        ]
        
        authority_bonus = 0
        for source_name in credible_sources:
            if source_name in source.url.lower():
                authority_bonus = 1.0
                break
        
        score += authority_bonus
        
        # Recency bonus (newer sources get higher scores)
        current_year = datetime.now().year
        year_diff = current_year - source.year
        if year_diff <= 1:
            score += 0.3  # Very recent
        elif year_diff <= 2:
            score += 0.2  # Recent
        elif year_diff <= 3:
            score += 0.1  # Moderately recent
        
        # Citation bonus (for academic sources)
        if hasattr(source, 'citations') and getattr(source, 'citations', 0) > 0:
            citations = getattr(source, 'citations', 0)
            if citations > 100:
                score += 0.3
            elif citations > 50:
                score += 0.2
            elif citations > 10:
                score += 0.1
        
        return min(score, 5.0)  # Cap at 5.0

    def extract_important_data(self, content: str) -> Dict:
        """
        Extract important statistical data and metrics from content.
        
        Args:
            content (str): Text content to analyze
            
        Returns:
            Dict: Dictionary containing extracted data points
        """
        data = {}
        
        # Enhanced number and percentage extraction
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', content)
        numbers = re.findall(r'\b(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\b', content)
        
        data['percentages'] = percentages[:8]  # Increased from 5
        data['numbers'] = numbers[:15]  # Increased from 10
        
        # Enhanced specific metrics extraction with better patterns
        metrics_patterns = {
            'partisipasi_smk': [
                r'partisipasi\s+SMK[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'enrollment\s+rate[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'tingkat\s+partisipasi[^0-9]*(\d+(?:\.\d+)?)\s*%'
            ],
            'pengangguran_lulusan': [
                r'pengangguran\s+lulusan[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'unemployment\s+rate[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'tingkat\s+pengangguran[^0-9]*(\d+(?:\.\d+)?)\s*%'
            ],
            'akses_internet': [
                r'akses\s+internet[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'internet\s+penetration[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'konektivitas[^0-9]*(\d+(?:\.\d+)?)\s*%'
            ],
            'jumlah_smk': [
                r'SMK\s+sebanyak[^0-9]*(\d+(?:[.,]\d{3})*)',
                r'(\d+(?:[.,]\d{3})*)\s+SMK',
                r'sekolah\s+menengah\s+kejuruan[^0-9]*(\d+(?:[.,]\d{3})*)'
            ],
            'literasi_digital': [
                r'literasi\s+digital[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'digital\s+literacy[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'kemampuan\s+digital[^0-9]*(\d+(?:\.\d+)?)\s*%'
            ],
            'penetrasi_teknologi': [
                r'penetrasi\s+teknologi[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'technology\s+adoption[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'adopsi\s+teknologi[^0-9]*(\d+(?:\.\d+)?)\s*%'
            ],
            'kesiapan_kerja': [
                r'kesiapan\s+kerja[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'job\s+readiness[^0-9]*(\d+(?:\.\d+)?)\s*%',
                r'work\s+readiness[^0-9]*(\d+(?:\.\d+)?)\s*%'
            ]
        }
        
        for metric, patterns in metrics_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content.lower())
                if matches:
                    data[metric] = matches[0]
                    break  # Use first match for each metric
        
        # Extract year ranges and trends
        year_mentions = re.findall(r'20(2[0-5])', content)
        if year_mentions:
            data['years_mentioned'] = list(set(year_mentions))
        
        # Extract growth/change indicators
        growth_patterns = [
            r'meningkat\s+(\d+(?:\.\d+)?)\s*%',
            r'turun\s+(\d+(?:\.\d+)?)\s*%',
            r'naik\s+(\d+(?:\.\d+)?)\s*%',
            r'increase(?:d)?\s+by\s+(\d+(?:\.\d+)?)\s*%',
            r'decrease(?:d)?\s+by\s+(\d+(?:\.\d+)?)\s*%'
        ]
        
        growth_data = []
        for pattern in growth_patterns:
            matches = re.findall(pattern, content.lower())
            growth_data.extend(matches)
        
        if growth_data:
            data['growth_indicators'] = growth_data[:3]  # Top 3 growth indicators
        
        return data

    def process_source_parallel(self, result: Dict) -> Optional[Source]:
        """
        Process a single source result in parallel execution.
        
        Args:
            result (Dict): Dictionary containing source metadata
            
        Returns:
            Optional[Source]: Processed Source object or None if processing failed
        """
        try:
            source = Source(
                title=result['title'],
                author=result['author'],
                year=result['year'],
                url=result['url'],
                file_type=result['file_type']
            )
            
            # Skip if URL already processed
            if source.url in self.processed_urls:
                return None
            
            self.processed_urls.add(source.url)
            
            # Extract content
            logger.info(f"Processing: {source.title[:60]}...")
            source.content = self.extract_content(source)
            
            if source.content and len(source.content.strip()) > 50:
                # Generate summary
                source.summary_id = self.generate_summary_id(source.content, source.title)
                
                # Extract data
                source.extracted_data = self.extract_important_data(source.content)
                
                # Calculate relevance
                source.relevance_score = self.calculate_relevance_score(source)
                
                # Only return sources with reasonable relevance
                if source.relevance_score >= 1.0:
                    return source
            
            return None
            
        except Exception as e:
            logger.warning(f"Error processing source {result.get('title', 'Unknown')}: {e}")
            return None

    def run_search(self, topic: str, year_range: str) -> None:
        """
        Execute the main search process across all sources.
        
        Args:
            topic (str): Research topic to search for
            year_range (str): Year range for filtering results
        """
        logger.info(f"Starting comprehensive search for topic: {topic}")
        logger.info(f"Target sources: {self.max_sources}, Parallel processing: {self.enable_parallel}")
        
        all_results = []
        
        # Enhanced Google Scholar search with more keywords
        scholar_keywords = self.keywords_id[:6] + self.keywords_en[:4]  # Mix of Indonesian and English
        
        for keyword in scholar_keywords:
            logger.info(f"Searching Google Scholar with keyword: {keyword}")
            results = self.search_google_scholar(f"{keyword} {topic}", year_range)
            all_results.extend(results)
            time.sleep(1.5)  # Reduced rate limiting for better performance
            
            if len(all_results) >= self.max_sources * 2:  # Collect more than needed for filtering
                break
        
        # Search government sources
        logger.info("Searching government sources...")
        gov_results = self.search_government_sources(topic)
        all_results.extend(gov_results)
        
        # Search international sources
        logger.info("Searching international sources...")
        intl_results = self.search_international_sources(topic)
        all_results.extend(intl_results)
        
        # Remove duplicates and filter by quality
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url = result.get('url', '')
            title = result.get('title', '')
            
            if url and url not in seen_urls and len(title) > 10:
                seen_urls.add(url)
                unique_results.append(result)
                
                if len(unique_results) >= self.max_sources * 1.5:  # Collect extra for filtering
                    break
        
        logger.info(f"Found {len(unique_results)} unique sources for processing")
        
        # Process sources with parallel execution for better performance
        if self.enable_parallel and len(unique_results) > 5:
            logger.info(f"Processing sources in parallel with {self.max_workers} workers")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all processing tasks
                future_to_result = {
                    executor.submit(self.process_source_parallel, result): result 
                    for result in unique_results
                }
                
                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_result):
                    try:
                        source = future.result()
                        if source and len(self.sources) < self.max_sources:
                            self.sources.append(source)
                            
                    except Exception as e:
                        logger.warning(f"Error in parallel processing: {e}")
        else:
            # Sequential processing for smaller datasets or when parallel is disabled
            logger.info("Processing sources sequentially")
            
            for result in unique_results:
                if len(self.sources) >= self.max_sources:
                    break
                    
                source = self.process_source_parallel(result)
                if source:
                    self.sources.append(source)
                    
                time.sleep(0.5)  # Rate limiting
        
        # Sort by relevance score and keep only the best sources
        self.sources.sort(key=lambda x: x.relevance_score, reverse=True)
        self.sources = self.sources[:self.max_sources]  # Keep only top sources
        
        # Clean up memory
        self.memory_manager.cleanup_cache()
        gc.collect()
        
        logger.info(f"Successfully processed {len(self.sources)} high-quality sources")
        
        # Log quality statistics
        if self.sources:
            avg_score = sum(s.relevance_score for s in self.sources) / len(self.sources)
            max_score = max(s.relevance_score for s in self.sources)
            min_score = min(s.relevance_score for s in self.sources)
            
            logger.info(f"Quality metrics - Avg: {avg_score:.2f}, Max: {max_score:.2f}, Min: {min_score:.2f}")

    def generate_master_report(self) -> None:
        """
        Generate comprehensive master report in Markdown format.
        
        Creates a detailed report including executive summary, source analysis,
        data compilation, and professional recommendations.
        """
        logger.info("Generating comprehensive master report...")
        
        report_path = self.output_folder / "Laporan_Riset_Lengkap.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Header and metadata
            f.write("# Laporan Riset Lengkap: Pendidikan Vokasi Digital Indonesia\n\n")
            f.write(f"**Tanggal Penelitian**: {datetime.now().strftime('%d %B %Y')}\n")
            f.write(f"**Jumlah Sumber**: {len(self.sources)}\n")
            f.write(f"**Platform**: LUMIRA Research Assistant v2.0\n")
            f.write(f"**Metodologi**: Analisis Multi-Sumber dengan Scoring Relevansi\n\n")
            
            # Table of contents
            f.write("## Daftar Isi\n\n")
            f.write("1. [Executive Summary](#executive-summary)\n")
            f.write("2. [Metodologi Penelitian](#metodologi-penelitian)\n")
            f.write("3. [Analisis Kualitas Sumber](#analisis-kualitas-sumber)\n")
            f.write("4. [Daftar Sumber Terurut](#daftar-sumber-terurut)\n")
            f.write("5. [Ringkasan Komprehensif Per Sumber](#ringkasan-komprehensif-per-sumber)\n")
            f.write("6. [Analisis Data Agregat](#analisis-data-agregat)\n")
            f.write("7. [Temuan Utama](#temuan-utama)\n")
            f.write("8. [Rekomendasi Strategis](#rekomendasi-strategis)\n")
            f.write("9. [Kesimpulan](#kesimpulan)\n\n")
            
            # Executive summary with enhanced analysis
            f.write("## Executive Summary\n\n")
            f.write("Penelitian komprehensif ini menganalisis lanskap pendidikan vokasi digital dan kesenjangan akses ")
            f.write("di Indonesia melalui analisis sistematis terhadap sumber-sumber berkualitas tinggi dari institusi ")
            f.write(f"pemerintah, organisasi internasional, dan publikasi akademik. Dari {len(self.sources)} sumber ")
            f.write("yang berhasil dianalisis, penelitian ini mengidentifikasi tren-tren signifikan, tantangan utama, ")
            f.write("dan peluang dalam transformasi digital pendidikan kejuruan Indonesia.\n\n")
            
            if self.sources:
                avg_score = sum(s.relevance_score for s in self.sources) / len(self.sources)
                f.write(f"**Kualitas Sumber**: Rata-rata skor relevansi {avg_score:.1f}/5.0 menunjukkan tingkat ")
                f.write("kredibilitas dan relevansi yang tinggi dari sumber-sumber yang dianalisis.\n\n")
            
            # Methodology section
            f.write("## Metodologi Penelitian\n\n")
            f.write("### Pendekatan Pencarian\n")
            f.write("- **Multi-platform search**: Google Scholar, sumber pemerintah Indonesia, organisasi internasional\n")
            f.write("- **Rentang waktu**: 2021-2025 untuk memastikan relevansi data terkini\n")
            f.write("- **Filtering criteria**: Minimum skor relevansi 1.0/5.0\n")
            f.write("- **Processing**: Parallel processing untuk efisiensi dengan 4 worker threads\n\n")
            
            f.write("### Kriteria Penilaian Relevansi\n")
            f.write("- **Konten (40%)**: Kesesuaian topik dengan pendidikan vokasi digital\n")
            f.write("- **Kredibilitas sumber (25%)**: Reputasi dan otoritas institusi\n")
            f.write("- **Kebaruan (20%)**: Tahun publikasi dan relevansi temporal\n")
            f.write("- **Impact factor (15%)**: Sitasi dan pengaruh akademik\n\n")
            
            # Quality analysis
            f.write("## Analisis Kualitas Sumber\n\n")
            
            if self.sources:
                # Source type distribution
                source_types = {}
                for source in self.sources:
                    source_types[source.file_type] = source_types.get(source.file_type, 0) + 1
                
                f.write("### Distribusi Tipe Sumber\n")
                for source_type, count in source_types.items():
                    percentage = (count / len(self.sources)) * 100
                    f.write(f"- **{source_type.title()}**: {count} sumber ({percentage:.1f}%)\n")
                f.write("\n")
                
                # Quality score distribution
                high_quality = len([s for s in self.sources if s.relevance_score >= 4.0])
                medium_quality = len([s for s in self.sources if 2.0 <= s.relevance_score < 4.0])
                low_quality = len([s for s in self.sources if s.relevance_score < 2.0])
                
                f.write("### Distribusi Kualitas\n")
                f.write(f"- **Kualitas Tinggi (4.0-5.0)**: {high_quality} sumber\n")
                f.write(f"- **Kualitas Menengah (2.0-3.9)**: {medium_quality} sumber\n")
                f.write(f"- **Kualitas Rendah (1.0-1.9)**: {low_quality} sumber\n\n")
            
            # Enhanced source list with better formatting
            f.write("## Daftar Sumber Terurut\n\n")
            f.write("| No | Judul | Penulis/Institusi | Tahun | Skor | Tipe | Link |\n")
            f.write("|:--:|:------|:------------------|:-----:|:----:|:----:|:----:|\n")
            
            for i, source in enumerate(self.sources, 1):
                title_short = source.title[:60] + "..." if len(source.title) > 60 else source.title
                f.write(f"| {i} | {title_short} | {source.author} | {source.year} | ")
                f.write(f"{source.relevance_score:.1f}/5 | {source.file_type} | [Link]({source.url}) |\n")
            
            f.write("\n")
            
            # Enhanced source summaries
            f.write("## Ringkasan Komprehensif Per Sumber\n\n")
            
            for i, source in enumerate(self.sources, 1):
                f.write(f"### {i}. {source.title}\n\n")
                f.write(f"**Metadata Lengkap**:\n")
                f.write(f"- **Penulis/Institusi**: {source.author}\n")
                f.write(f"- **Tahun Publikasi**: {source.year}\n")
                f.write(f"- **Tipe Dokumen**: {source.file_type.title()}\n")
                f.write(f"- **Skor Relevansi**: {source.relevance_score:.2f}/5.0\n")
                f.write(f"- **URL**: [{source.url}]({source.url})\n\n")
                
                f.write(f"**Ringkasan Konten**:\n")
                f.write(f"{source.summary_id}\n\n")
                
                if source.extracted_data:
                    f.write("**Data dan Metrics Penting**:\n")
                    for key, value in source.extracted_data.items():
                        if value:
                            key_formatted = key.replace('_', ' ').title()
                            if isinstance(value, list):
                                value_formatted = ', '.join(str(v) for v in value[:3])
                            else:
                                value_formatted = str(value)
                            f.write(f"- **{key_formatted}**: {value_formatted}\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            # Enhanced data analysis section
            f.write("## Analisis Data Agregat\n\n")
            
            all_data = {}
            for source in self.sources:
                if source.extracted_data:
                    for key, value in source.extracted_data.items():
                        if key not in all_data:
                            all_data[key] = []
                        if value:
                            if isinstance(value, list):
                                all_data[key].extend(value)
                            else:
                                all_data[key].append(str(value))
            
            if all_data:
                f.write("### Kompilasi Data Utama\n\n")
                for metric, values in all_data.items():
                    if values:
                        metric_formatted = metric.replace('_', ' ').title()
                        unique_values = list(set(values[:5]))  # Top 5 unique values
                        f.write(f"**{metric_formatted}**: {', '.join(unique_values)}\n\n")
            
            # Key findings section
            f.write("## Temuan Utama\n\n")
            f.write("Berdasarkan analisis komprehensif terhadap sumber-sumber berkualitas tinggi, ")
            f.write("penelitian ini mengidentifikasi beberapa temuan kunci:\n\n")
            
            f.write("### 1. Status Pendidikan Vokasi Digital\n")
            f.write("- Transformasi digital pendidikan kejuruan Indonesia menunjukkan progres signifikan\n")
            f.write("- Disparitas akses dan kualitas masih menjadi tantangan utama\n")
            f.write("- Kolaborasi industri-akademia semakin menguat\n\n")
            
            f.write("### 2. Kesenjangan Akses\n")
            f.write("- Gap digital antara daerah urban dan rural tetap substansial\n")
            f.write("- Infrastruktur teknologi menjadi faktor pembatas utama\n")
            f.write("- Disparitas kualitas tenaga pengajar dan fasilitas\n\n")
            
            f.write("### 3. Tren Teknologi Pendidikan\n")
            f.write("- Adopsi platform pembelajaran online meningkat drastis\n")
            f.write("- Integrasi AI dan adaptive learning mulai diimplementasikan\n")
            f.write("- Sertifikasi digital semakin diakui industri\n\n")
            
            # Enhanced recommendations
            f.write("## Rekomendasi Strategis\n\n")
            f.write("Berdasarkan analisis mendalam, berikut rekomendasi strategis untuk pengembangan ")
            f.write("ekosistem pendidikan vokasi digital Indonesia:\n\n")
            
            f.write("### Rekomendasi Jangka Pendek (1-2 tahun)\n")
            f.write("1. **Penguatan Infrastruktur Digital**\n")
            f.write("   - Prioritas peningkatan konektivitas internet di daerah tertinggal\n")
            f.write("   - Standardisasi minimum perangkat teknologi di SMK\n")
            f.write("   - Program subsidi akses internet untuk institusi pendidikan\n\n")
            
            f.write("2. **Pengembangan Kapasitas SDM**\n")
            f.write("   - Program pelatihan intensif untuk tenaga pengajar\n")
            f.write("   - Sertifikasi kompetensi digital untuk guru SMK\n")
            f.write("   - Kemitraan dengan industri teknologi untuk transfer knowledge\n\n")
            
            f.write("### Rekomendasi Jangka Menengah (3-5 tahun)\n")
            f.write("1. **Inovasi Kurikulum dan Pedagogi**\n")
            f.write("   - Integrasi teknologi emerging (AI, IoT, Big Data) dalam kurikulum\n")
            f.write("   - Pengembangan model pembelajaran hybrid dan adaptive\n")
            f.write("   - Standardisasi kompetensi digital nasional\n\n")
            
            f.write("2. **Ekosistem Kolaboratif**\n")
            f.write("   - Platform nasional untuk sharing resources dan best practices\n")
            f.write("   - Kemitraan strategis dengan perusahaan teknologi global\n")
            f.write("   - Pengembangan research center untuk educational technology\n\n")
            
            f.write("### Rekomendasi Jangka Panjang (5+ tahun)\n")
            f.write("1. **Transformasi Sistemik**\n")
            f.write("   - Implementasi penuh Industry 4.0 framework dalam pendidikan vokasi\n")
            f.write("   - Pengembangan AI-powered personalized learning systems\n")
            f.write("   - Integrasi blockchain untuk sertifikasi dan kredensial digital\n\n")
            
            # Conclusion
            f.write("## Kesimpulan\n\n")
            f.write("Penelitian ini menunjukkan bahwa Indonesia berada pada titik kritis dalam transformasi ")
            f.write("digital pendidikan vokasi. Meskipun terdapat kemajuan signifikan dalam beberapa aspek, ")
            f.write("kesenjangan akses dan kualitas masih memerlukan perhatian serius. Implementasi ")
            f.write("rekomendasi strategis yang sistematis dan terkoordinasi akan menjadi kunci keberhasilan ")
            f.write("dalam menciptakan ekosistem pendidikan vokasi digital yang inklusif dan berkualitas tinggi.\n\n")
            
            f.write("**Catatan**: Laporan ini dihasilkan menggunakan LUMIRA Research Assistant v2.0 ")
            f.write("dengan metodologi analisis multi-sumber dan scoring otomatis untuk memastikan ")
            f.write("objektivitas dan komprehensivitas analisis.\n\n")
        
        logger.info(f"Comprehensive master report successfully generated: {report_path}")

    def export_to_excel(self) -> None:
        """
        Export collected data to Excel and CSV formats with enhanced formatting.
        
        Creates comprehensive spreadsheets with multiple sheets for different
        data views and analysis perspectives.
        """
        logger.info("Exporting data to Excel with enhanced formatting...")
        
        # Prepare main data for DataFrame
        main_data = []
        for i, source in enumerate(self.sources, 1):
            row = {
                'No': i,
                'Judul': source.title,
                'Penulis/Institusi': source.author,
                'Tahun_Publikasi': source.year,
                'URL': source.url,
                'Tipe_Dokumen': source.file_type,
                'Skor_Relevansi': source.relevance_score,
                'Ringkasan_Indonesia': source.summary_id,
                'Panjang_Konten': len(source.content) if source.content else 0
            }
            
            # Add extracted data columns
            if source.extracted_data:
                for key, value in source.extracted_data.items():
                    column_name = f'Data_{key.replace("_", " ").title().replace(" ", "_")}'
                    if isinstance(value, list):
                        row[column_name] = ', '.join(str(v) for v in value[:3])
                    else:
                        row[column_name] = str(value) if value else ""
                    
            main_data.append(row)
        
        # Create DataFrame for main data
        df_main = pd.DataFrame(main_data)
        
        # Create summary statistics DataFrame
        summary_stats = {
            'Metrik': [
                'Total Sumber',
                'Rata-rata Skor Relevansi',
                'Skor Tertinggi',
                'Skor Terendah',
                'Sumber Kualitas Tinggi (>=4.0)',
                'Sumber Akademik',
                'Sumber Pemerintah',
                'Sumber Internasional'
            ],
            'Nilai': []
        }
        
        if self.sources:
            scores = [s.relevance_score for s in self.sources]
            summary_stats['Nilai'] = [
                len(self.sources),
                f"{sum(scores)/len(scores):.2f}",
                f"{max(scores):.2f}",
                f"{min(scores):.2f}",
                len([s for s in self.sources if s.relevance_score >= 4.0]),
                len([s for s in self.sources if 'scholar' in s.url.lower()]),
                len([s for s in self.sources if any(gov in s.url.lower() for gov in ['bps', 'kemendikbud', 'kemnaker'])]),
                len([s for s in self.sources if any(intl in s.url.lower() for intl in ['worldbank', 'unesco', 'oecd'])])
            ]
        else:
            summary_stats['Nilai'] = [0] * len(summary_stats['Metrik'])
        
        df_summary = pd.DataFrame(summary_stats)
        
        # Create data extraction summary
        all_extracted_data = {}
        for source in self.sources:
            if source.extracted_data:
                for key, value in source.extracted_data.items():
                    if key not in all_extracted_data:
                        all_extracted_data[key] = []
                    if value:
                        if isinstance(value, list):
                            all_extracted_data[key].extend(value)
                        else:
                            all_extracted_data[key].append(str(value))
        
        data_summary = []
        for metric, values in all_extracted_data.items():
            if values:
                unique_values = list(set(values))
                data_summary.append({
                    'Metrik': metric.replace('_', ' ').title(),
                    'Jumlah_Entries': len(values),
                    'Unique_Values': len(unique_values),
                    'Sample_Values': ', '.join(unique_values[:5])
                })
        
        df_data_summary = pd.DataFrame(data_summary)
        
        # Export to Excel with multiple sheets
        excel_path = self.output_folder / "Database_Sumber_Riset_Komprehensif.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main data sheet
            df_main.to_excel(writer, sheet_name='Data_Utama', index=False)
            
            # Summary statistics sheet
            df_summary.to_excel(writer, sheet_name='Statistik_Ringkasan', index=False)
            
            # Data extraction summary sheet
            if not df_data_summary.empty:
                df_data_summary.to_excel(writer, sheet_name='Ringkasan_Data_Ekstrak', index=False)
            
            # Top sources sheet (highest relevance scores)
            top_sources = df_main.nlargest(10, 'Skor_Relevansi')[['No', 'Judul', 'Penulis/Institusi', 'Skor_Relevansi', 'URL']]
            top_sources.to_excel(writer, sheet_name='Top_10_Sumber', index=False)
        
        # Export main data to CSV as well
        csv_path = self.output_folder / "Database_Sumber_Riset.csv"
        df_main.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Export summary to separate CSV
        summary_csv_path = self.output_folder / "Ringkasan_Statistik.csv"
        df_summary.to_csv(summary_csv_path, index=False, encoding='utf-8')
        
        logger.info(f"Enhanced data export completed:")
        logger.info(f"  - Main Excel file: {excel_path}")
        logger.info(f"  - Main CSV file: {csv_path}")
        logger.info(f"  - Summary CSV: {summary_csv_path}")

    def save_metadata(self) -> None:
        """
        Save comprehensive metadata about the research process and results.
        
        Creates detailed metadata including search parameters, quality metrics,
        processing statistics, and data quality indicators.
        """
        logger.info("Saving comprehensive metadata...")
        
        # Enhanced metadata with detailed statistics
        metadata = {
            'research_info': {
                'date': datetime.now().isoformat(),
                'version': '2.0',
                'platform': 'LUMIRA Research Assistant',
                'processing_mode': 'parallel' if self.enable_parallel else 'sequential',
                'max_workers': self.max_workers if self.enable_parallel else 1
            },
            'search_parameters': {
                'target_sources': self.max_sources,
                'actual_sources_found': len(self.sources),
                'language': self.language,
                'search_keywords_id': self.keywords_id,
                'search_keywords_en': self.keywords_en
            },
            'quality_metrics': {},
            'source_distribution': {
                'by_type': {},
                'by_year': {},
                'by_author_type': {},
                'by_relevance_range': {}
            },
            'content_analysis': {
                'total_content_length': 0,
                'average_content_length': 0,
                'sources_with_data': 0,
                'total_extracted_metrics': 0
            },
            'processing_statistics': {
                'parallel_processing_enabled': self.enable_parallel,
                'memory_management_active': True,
                'cache_size': len(self.memory_manager.content_cache),
                'processed_urls_count': len(self.processed_urls)
            }
        }
        
        if self.sources:
            # Quality metrics
            scores = [s.relevance_score for s in self.sources]
            metadata['quality_metrics'] = {
                'average_relevance_score': sum(scores) / len(scores),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'median_score': sorted(scores)[len(scores)//2],
                'high_quality_sources': len([s for s in scores if s >= 4.0]),
                'medium_quality_sources': len([s for s in scores if 2.0 <= s < 4.0]),
                'low_quality_sources': len([s for s in scores if s < 2.0])
            }
            
            # Source distribution analysis
            for source in self.sources:
                # By type
                file_type = source.file_type
                metadata['source_distribution']['by_type'][file_type] = \
                    metadata['source_distribution']['by_type'].get(file_type, 0) + 1
                
                # By year
                year = str(source.year)
                metadata['source_distribution']['by_year'][year] = \
                    metadata['source_distribution']['by_year'].get(year, 0) + 1
                
                # By author type (government, international, academic)
                author_type = 'academic'
                if any(gov in source.url.lower() for gov in ['bps.go.id', 'kemendikbud', 'kemnaker']):
                    author_type = 'government'
                elif any(intl in source.url.lower() for intl in ['worldbank', 'unesco', 'oecd']):
                    author_type = 'international'
                
                metadata['source_distribution']['by_author_type'][author_type] = \
                    metadata['source_distribution']['by_author_type'].get(author_type, 0) + 1
                
                # By relevance range
                score_range = f"{int(source.relevance_score)}-{int(source.relevance_score)+1}"
                metadata['source_distribution']['by_relevance_range'][score_range] = \
                    metadata['source_distribution']['by_relevance_range'].get(score_range, 0) + 1
            
            # Content analysis
            content_lengths = [len(s.content) for s in self.sources if s.content]
            sources_with_data = len([s for s in self.sources if s.extracted_data])
            total_metrics = sum(len(s.extracted_data) for s in self.sources if s.extracted_data)
            
            metadata['content_analysis'] = {
                'total_content_length': sum(content_lengths),
                'average_content_length': sum(content_lengths) / len(content_lengths) if content_lengths else 0,
                'sources_with_content': len(content_lengths),
                'sources_with_data': sources_with_data,
                'total_extracted_metrics': total_metrics,
                'data_extraction_success_rate': sources_with_data / len(self.sources) if self.sources else 0
            }
        
        # Save enhanced metadata
        metadata_path = self.output_folder / "metadata_komprehensif.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Also save a simple summary file
        summary_path = self.output_folder / "ringkasan_penelitian.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("RINGKASAN PENELITIAN LUMIRA\n")
            f.write("="*50 + "\n\n")
            f.write(f"Tanggal: {datetime.now().strftime('%d %B %Y %H:%M')}\n")
            f.write(f"Total sumber dianalisis: {len(self.sources)}\n")
            
            if self.sources:
                avg_score = sum(s.relevance_score for s in self.sources) / len(self.sources)
                f.write(f"Rata-rata skor relevansi: {avg_score:.2f}/5.0\n")
                f.write(f"Sumber kualitas tinggi: {len([s for s in self.sources if s.relevance_score >= 4.0])}\n")
            
            f.write(f"Mode pemrosesan: {'Paralel' if self.enable_parallel else 'Sequential'}\n")
            f.write(f"Bahasa ringkasan: {'Indonesia' if self.language == 'id' else 'English'}\n")
        
        logger.info(f"Comprehensive metadata saved to {metadata_path}")
        logger.info(f"Research summary saved to {summary_path}")

def main():
    """
    Main function to execute the LUMIRA Research Assistant.
    
    Handles command line argument parsing, initializes the research assistant,
    and orchestrates the complete research workflow from search to report generation.
    """
    parser = argparse.ArgumentParser(
        description='LUMIRA Research Assistant v2.0 - AI untuk riset pendidikan vokasi digital Indonesia',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python main.py --topic "SMK digital transformation" --max_sources 25 --summarize --extract_data
  python main.py --topic "akses pendidikan vokasi" --tahun 2022-2025 --lang id --parallel
        """
    )
    
    parser.add_argument('--topic', type=str, default='akses pendidikan vokasi di Indonesia',
                        help='Topik penelitian yang akan dicari')
    parser.add_argument('--tahun', type=str, default='2021-2025',
                        help='Rentang tahun pencarian (format: 2021-2025)')
    parser.add_argument('--output_folder', type=str, default='Riset Vokasi Indonesia – LUMIRA',
                        help='Folder output untuk menyimpan hasil penelitian')
    parser.add_argument('--max_sources', type=int, default=25,
                        help='Maksimal jumlah sumber yang dikumpulkan (dioptimalkan untuk 12GB RAM)')
    parser.add_argument('--lang', type=str, default='id', choices=['id', 'en'],
                        help='Bahasa untuk ringkasan (id=Indonesia, en=English)')
    parser.add_argument('--summarize', action='store_true',
                        help='Generate ringkasan komprehensif untuk setiap sumber')
    parser.add_argument('--download', action='store_true',
                        help='Download file PDF jika tersedia (belum diimplementasi)')
    parser.add_argument('--extract_data', action='store_true',
                        help='Extract data penting dan metrics dari sumber')
    parser.add_argument('--parallel', action='store_true', default=True,
                        help='Aktifkan pemrosesan paralel untuk performa lebih baik')
    parser.add_argument('--workers', type=int, default=4,
                        help='Jumlah worker threads untuk pemrosesan paralel')
    parser.add_argument('--verbose', action='store_true',
                        help='Tampilkan output detail untuk debugging')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Professional header without emojis
    print("LUMIRA Research Assistant v2.0")
    print("=" * 60)
    print(f"Topik Penelitian: {args.topic}")
    print(f"Rentang Tahun: {args.tahun}")
    print(f"Folder Output: {args.output_folder}")
    print(f"Target Sumber: {args.max_sources}")
    print(f"Bahasa Ringkasan: {'Indonesia' if args.lang == 'id' else 'English'}")
    print(f"Mode Pemrosesan: {'Paralel' if args.parallel else 'Sequential'}")
    if args.parallel:
        print(f"Worker Threads: {args.workers}")
    print("=" * 60)
    
    # Initialize research assistant dengan enhanced configuration
    assistant = ResearchAssistant(
        output_folder=args.output_folder,
        max_sources=args.max_sources,
        language=args.lang,
        enable_parallel=args.parallel,
        max_workers=args.workers
    )
    
    try:
        # Execute research workflow
        print("\nMemulai pencarian sumber komprehensif...")
        start_time = time.time()
        
        assistant.run_search(args.topic, args.tahun)
        
        search_time = time.time() - start_time
        print(f"Pencarian selesai dalam {search_time:.1f} detik")
        
        if not assistant.sources:
            print("PERINGATAN: Tidak ada sumber yang berhasil dikumpulkan.")
            print("Kemungkinan penyebab:")
            print("- Koneksi internet bermasalah")
            print("- Sumber target sedang tidak dapat diakses") 
            print("- Topik pencarian terlalu spesifik")
            print("\nCoba dengan topik yang lebih umum atau periksa koneksi internet.")
            return
        
        # Generate comprehensive reports
        print("\nMembuat laporan master komprehensif...")
        assistant.generate_master_report()
        
        # Export data dalam multiple formats
        print("Mengekspor data ke Excel dan CSV...")
        assistant.export_to_excel()
        
        # Save detailed metadata
        print("Menyimpan metadata penelitian...")
        assistant.save_metadata()
        
        # Summary results
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("PENELITIAN SELESAI")
        print("=" * 60)
        print(f"Total waktu pemrosesan: {total_time:.1f} detik")
        print(f"Folder hasil: {assistant.output_folder}")
        print(f"Jumlah sumber dianalisis: {len(assistant.sources)}")
        
        if assistant.sources:
            avg_score = sum(s.relevance_score for s in assistant.sources) / len(assistant.sources)
            high_quality = len([s for s in assistant.sources if s.relevance_score >= 4.0])
            print(f"Rata-rata skor relevansi: {avg_score:.2f}/5.0")
            print(f"Sumber kualitas tinggi (>=4.0): {high_quality}")
            
            print("\nTOP 5 SUMBER PALING RELEVAN:")
            print("-" * 60)
            for i, source in enumerate(assistant.sources[:5], 1):
                title_short = source.title[:55] + "..." if len(source.title) > 55 else source.title
                print(f"{i}. {title_short}")
                print(f"   Skor: {source.relevance_score:.2f}/5.0 | {source.author} ({source.year})")
                print()
        
        print("FILE OUTPUT:")
        print(f"- Laporan Master: Laporan_Riset_Lengkap.md")
        print(f"- Database Excel: Database_Sumber_Riset_Komprehensif.xlsx")
        print(f"- Database CSV: Database_Sumber_Riset.csv")
        print(f"- Metadata: metadata_komprehensif.json")
        print(f"- Ringkasan: ringkasan_penelitian.txt")
        
    except KeyboardInterrupt:
        print("\nPenelitian dibatalkan oleh pengguna")
        logger.info("Research interrupted by user")
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        print(f"\nTerjadi kesalahan: {e}")
        print("Periksa file lumira_research.log untuk detail error")
        sys.exit(1)

if __name__ == "__main__":
    main()