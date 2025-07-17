# GoogleScholar-Scraper
This is a simple guide to scrape results from Google Scholar. The Python script (attached) opens an intuitive GUI that allows the user to search, view and download results I.e. Articles in .csv and .xls format. This is made to run on Terminal thus can be easily used on MacBook and Linux systems. 

Installation Requirements

	Install the required dependencies on your MacBook via Terminal.
	bash
	# Install required packages
	pip3 install requests beautifulsoup4 lxml pandas openpyxl

	# Optional: For advanced proxy support
	pip3 install selenium webdriver-manager


Executing the script

1. Change the working directory to the folder where you have saved the python script and intend to save the output results.
   
	bash

	cd /usr/path_to_your_folder

 2. Make it Executable

	bash
	chmod +x google_scholar_scraper.py


3. Run via Terminal
	
 	bash

	python3 google_scholar_scraper.py

	

Et voilà, the intuitive GUI of scraper will guide you to what you are seeking!
