# Ive made a change!
from bs4 import BeautifulSoup
import urllib.request
import time
import zipfile
import os

# Record the start time
start_time = time.time()

baseline_url = "https://www.europarl.europa.eu/news/en/press-room"
seed_url = "https://www.europarl.europa.eu/news/en/press-room/page/"
n = -1
urls = []           # Queue of URLs to crawl
seen = []           # Stack of URLs seen so far
crisis_press_releases = []  # Stores URLs that include crisis
crisis_press_release_soup = [] # Stores the HTML content of each press release

while len(crisis_press_releases) < 10:
    
    n+=1 # Start counter for the seed url ending at 0

    try:
        curr_url = seed_url + str(n)  # Create our first page to search through
        seen.append(curr_url)   # Add it to the seen list
        req = urllib.request.Request(curr_url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urllib.request.urlopen(req).read()  # Read the content from the webpage

        soup = BeautifulSoup(webpage, 'html.parser')  # Create a BeautifulSoup object

        # Find child URLs and add them to the queue if they meet the criteria
        for tag in soup.find_all('a', href=True):
            child_url = tag['href']
            child_url = urllib.parse.urljoin(baseline_url, child_url)
            if child_url.startswith(baseline_url) == True and child_url not in seen:
                urls.append(child_url)
                seen.append(child_url)      

        while len(urls)>0: # This goes through all the URLS we just got above in each round

            # Check if the page source contains the specific anchor tag for "Press Release"
            curr_press = urls.pop(0)
            req = urllib.request.Request(curr_press, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urllib.request.urlopen(req).read()  # Read the content from the webpage

            soup = BeautifulSoup(webpage, 'html.parser')  # Create a BeautifulSoup object

            if soup.find('span', class_='ep_name', text='Plenary session'):     # If the website satisfies our conditions...
            # Check if the page source contains the word "crisis" in title or text
                title = soup.find('title') 
                subtitle = soup.find('meta', attrs={'name': 'description'})
                paragraphs = soup.find_all('p', class_="ep-wysiwig_paragraph")
                
                if "crisis" in title.get_text().lower():
                    crisis_press_releases.append(curr_press)  # Add the URL to the list of crisis plenary session texts if "crisis" is in the title
                    print(len(crisis_press_releases))
                    crisis_press_release_soup.append(soup)

                elif "crisis" in subtitle.get_text().lower():
                    crisis_press_releases.append(curr_press)  # Add the URL to the list of crisis plenary session texts if "crisis" is in the subtitle
                    print(len(crisis_press_releases))
                    crisis_press_release_soup.append(soup)

                for paragraph in paragraphs:
                    if "crisis" in paragraph.get_text().lower() and curr_press not in crisis_press_releases:
                        crisis_press_releases.append(curr_press)  # Add the URL to the list of crisis plenary session texts if "crisis" is in the body
                        print(len(crisis_press_releases))
                        crisis_press_release_soup.append(soup)

    except Exception as ex:
        continue

print("URLs with 'Plenary Session' anchor tag and the word 'crisis' in title or text:")
for crisis_url in crisis_press_releases:
    print(crisis_url) # Result

# Calculate the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")

# Soup text files
# Create a zip file to store the BeautifulSoup objects
with zipfile.ZipFile('eu_plenary_session_crisis.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    # For the list of BeautifulSoup objects called 'crisis_press_release_soup'
    for idx, soup in enumerate(crisis_press_release_soup):
        # Serialize the BeautifulSoup object to a string
        soup_str = str(soup)
        idx = idx + 1

        # Define a filename based on the index
        filename = f"eu_plenary_session_crisis_{idx}.txt"

        # Add the serialized soup string as a new file in the zip archive
        zipf.writestr(filename, soup_str)

        print(f"Saved {filename} to zip file")

print("Serialization and saving to zip file complete.")
