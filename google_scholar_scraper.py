#!/usr/bin/env python3
"""
Google Scholar Scraper with Boolean Operators and GUI
Designed for M1 MacBook - Educational Purpose Only
"""

import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import time
import random
import csv
import pandas as pd
import urllib.parse
import threading
from datetime import datetime

class GoogleScholarScraper:
    def __init__(self):
        self.base_url = "https://scholar.google.com/scholar"
        self.session = requests.Session()
        self.results = []
        
        # User-agent rotation to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    def create_boolean_query(self, keywords, operator="AND"):
        """Create Google Scholar query with Boolean operators"""
        if operator.upper() == "AND":
            query = " AND ".join([f'"{kw.strip()}"' for kw in keywords])
        elif operator.upper() == "OR":
            query = " OR ".join([f'"{kw.strip()}"' for kw in keywords])
        else:
            query = " ".join(keywords)
        return query
    
    def get_random_delay(self, min_delay=2, max_delay=5):
        """Random delay to avoid rate limiting"""
        return random.uniform(min_delay, max_delay)
    
    def make_request(self, url, params=None):
        """Make HTTP request with anti-blocking measures"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            time.sleep(self.get_random_delay())
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def extract_paper_data(self, paper_div):
        """Extract data from individual paper result"""
        data = {
            'title': '',
            'authors': '',
            'journal': '',
            'year': '',
            'citations': '',
            'doi': '',
            'url': '',
            'abstract': ''
        }
        
        try:
            # Title and URL
            title_tag = paper_div.find('h3', class_='gs_rt')
            if title_tag:
                data['title'] = title_tag.get_text().strip()
                link_tag = title_tag.find('a')
                if link_tag and link_tag.get('href'):
                    data['url'] = link_tag['href']
            
            # Authors, Journal, Year
            author_info = paper_div.find('div', class_='gs_a')
            if author_info:
                author_text = author_info.get_text()
                data['authors'] = author_text.strip()
                
                # Try to extract year
                import re
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', author_text)
                if year_match:
                    data['year'] = year_match.group(1)
            
            # Citations
            citation_div = paper_div.find('div', class_='gs_fl')
            if citation_div:
                citation_links = citation_div.find_all('a')
                for link in citation_links:
                    if 'Cited by' in link.get_text():
                        citation_text = link.get_text()
                        citation_count = citation_text.replace('Cited by ', '')
                        data['citations'] = citation_count
                        break
            
            # Abstract/Snippet
            abstract_div = paper_div.find('div', class_='gs_rs')
            if abstract_div:
                data['abstract'] = abstract_div.get_text().strip()
        
        except Exception as e:
            print(f"Error extracting paper data: {e}")
        
        return data
    
    def scrape_papers(self, keywords, boolean_operator="AND", max_results=100, year_from=2015, year_to=2025, progress_callback=None):
        """Main scraping function"""
        query = self.create_boolean_query(keywords, boolean_operator)
        self.results = []
        
        params = {
            'q': query,
            'as_ylo': year_from,
            'as_yhi': year_to,
            'start': 0
        }
        
        papers_per_page = 10
        total_pages = (max_results + papers_per_page - 1) // papers_per_page
        
        for page in range(total_pages):
            if progress_callback:
                progress_callback(f"Scraping page {page + 1} of {total_pages}...")
            
            params['start'] = page * papers_per_page
            response = self.make_request(self.base_url, params)
            
            if not response or response.status_code != 200:
                print(f"Failed to get page {page + 1}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            paper_divs = soup.find_all('div', class_='gs_ri')
            
            if not paper_divs:
                print("No more results found")
                break
            
            for paper_div in paper_divs:
                paper_data = self.extract_paper_data(paper_div)
                if paper_data['title']:
                    self.results.append(paper_data)
                    if len(self.results) >= max_results:
                        break
            
            if len(self.results) >= max_results:
                break
        
        return self.results
    
    def save_to_csv(self, filename):
        """Save results to CSV file"""
        if not self.results:
            return False
        
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False, encoding='utf-8')
        return True
    
    def save_to_excel(self, filename):
        """Save results to Excel file"""
        if not self.results:
            return False
        
        df = pd.DataFrame(self.results)
        df.to_excel(filename, index=False, engine='openpyxl')
        return True

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Scholar Scraper with Boolean Operators")
        self.root.geometry("800x700")
        
        self.scraper = GoogleScholarScraper()
        self.setup_gui()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Keywords input
        ttk.Label(main_frame, text="Keywords (comma-separated):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keywords_entry = tk.Text(main_frame, height=3, width=60)
        self.keywords_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.keywords_entry.insert('1.0', 'machine learning, artificial intelligence, deep learning')
        
        # Boolean operator
        ttk.Label(main_frame, text="Boolean Operator:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.boolean_var = tk.StringVar(value="AND")
        boolean_frame = ttk.Frame(main_frame)
        boolean_frame.grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(boolean_frame, text="AND", variable=self.boolean_var, value="AND").pack(side=tk.LEFT)
        ttk.Radiobutton(boolean_frame, text="OR", variable=self.boolean_var, value="OR").pack(side=tk.LEFT, padx=10)
        
        # Year range
        year_frame = ttk.Frame(main_frame)
        year_frame.grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(year_frame, text="Year From:").pack(side=tk.LEFT)
        self.year_from = tk.StringVar(value="2015")
        ttk.Entry(year_frame, textvariable=self.year_from, width=6).pack(side=tk.LEFT, padx=5)
        ttk.Label(year_frame, text="Year To:").pack(side=tk.LEFT, padx=10)
        self.year_to = tk.StringVar(value="2025")
        ttk.Entry(year_frame, textvariable=self.year_to, width=6).pack(side=tk.LEFT, padx=5)
        
        # Max results
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Label(results_frame, text="Max Results:").pack(side=tk.LEFT)
        self.max_results = tk.StringVar(value="50")
        ttk.Entry(results_frame, textvariable=self.max_results, width=6).pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, sticky=tk.W, pady=10)
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Save CSV", command=self.save_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Excel", command=self.save_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to scrape...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=7, column=0, sticky=tk.W, pady=5)
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Results display
        ttk.Label(main_frame, text="Results:").grid(row=9, column=0, sticky=tk.W, pady=(10, 5))
        self.results_text = scrolledtext.ScrolledText(main_frame, height=20, width=80)
        self.results_text.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(10, weight=1)
    
    def update_progress(self, message):
        """Update progress message"""
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def start_scraping(self):
        """Start scraping in a separate thread"""
        keywords_text = self.keywords_entry.get('1.0', tk.END).strip()
        if not keywords_text:
            messagebox.showerror("Error", "Please enter keywords")
            return
        
        keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        boolean_operator = self.boolean_var.get()
        year_from = int(self.year_from.get())
        year_to = int(self.year_to.get())
        max_results = int(self.max_results.get())
        
        self.start_button.config(state='disabled')
        self.progress_bar.start()
        
        # Run scraping in separate thread
        thread = threading.Thread(
            target=self.run_scraping,
            args=(keywords, boolean_operator, max_results, year_from, year_to)
        )
        thread.daemon = True
        thread.start()
    
    def run_scraping(self, keywords, boolean_operator, max_results, year_from, year_to):
        """Run scraping process"""
        try:
            results = self.scraper.scrape_papers(
                keywords=keywords,
                boolean_operator=boolean_operator,
                max_results=max_results,
                year_from=year_from,
                year_to=year_to,
                progress_callback=self.update_progress
            )
            
            self.display_results(results)
            self.update_progress(f"Scraping completed! Found {len(results)} papers.")
            
        except Exception as e:
            self.update_progress(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Scraping failed: {str(e)}")
        
        finally:
            self.progress_bar.stop()
            self.start_button.config(state='normal')
    
    def display_results(self, results):
        """Display results in the text widget"""
        self.results_text.delete('1.0', tk.END)
        
        for i, paper in enumerate(results, 1):
            result_text = f"{i}. {paper['title']}\n"
            result_text += f"   Authors: {paper['authors']}\n"
            result_text += f"   Year: {paper['year']}\n"
            result_text += f"   Citations: {paper['citations']}\n"
            result_text += f"   URL: {paper['url']}\n"
            result_text += f"   Abstract: {paper['abstract'][:200]}...\n"
            result_text += "-" * 80 + "\n\n"
            
            self.results_text.insert(tk.END, result_text)
    
    def save_csv(self):
        """Save results to CSV"""
        if not self.scraper.results:
            messagebox.showwarning("Warning", "No results to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            if self.scraper.save_to_csv(filename):
                messagebox.showinfo("Success", f"Results saved to {filename}")
            else:
                messagebox.showerror("Error", "Failed to save file")
    
    def save_excel(self):
        """Save results to Excel"""
        if not self.scraper.results:
            messagebox.showwarning("Warning", "No results to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if filename:
            if self.scraper.save_to_excel(filename):
                messagebox.showinfo("Success", f"Results saved to {filename}")
            else:
                messagebox.showerror("Error", "Failed to save file")
    
    def clear_results(self):
        """Clear results"""
        self.results_text.delete('1.0', tk.END)
        self.scraper.results = []
        self.update_progress("Results cleared. Ready to scrape...")

def main():
    root = tk.Tk()
    app = ScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
