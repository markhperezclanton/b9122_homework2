from bs4 import BeautifulSoup
import urllib.request
import time
import zipfile
import os

# Record the start time
start_time = time.time()

# Custom sorting key function
def custom_sort_key(item):
# Check if the item ends with "berry"
    if item.endswith(".doc.htm"):
        return (0, item)  # Assign a tuple (0, item) for items ending with ".doc.htm"
    else:
        return (1, item)  # Assign a tuple (1, item) for other items

seed_url = "https://press.un.org/en"

urls = [seed_url]           # Queue of URLs to crawl
seen = [seed_url]           # Stack of URLs seen so far
opened = []                 # List to keep track of visited URLs
crisis_press_releases = []  # Store URLs that meet the specified criteria
crisis_press_release_soup = [] # Stores the HTML content of each press release

print("Starting with url=" + str(urls))

while len(crisis_press_releases) < 2:

    try:
        # Sort the list using the custom sorting key
        urls = sorted(urls, key=custom_sort_key)

        curr_url = urls.pop(0)  # Extract the first element from urls

        req = urllib.request.Request(curr_url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urllib.request.urlopen(req).read()  # Read the content from the webpage
        opened.append(curr_url)  # Add the current URL to the opened list

        soup = BeautifulSoup(webpage, 'html.parser')  # Create a BeautifulSoup object

        # Check if the page source contains the specific anchor tag for "Press Release"
        if soup.find('a', href='/en/press-release', hreflang='en'):
            # Check if the page source contains the word "crisis" in title or text
            title_tag = soup.find('title')
            body_div = soup.find('div', class_="field field--name-body")
            if "crisis" in title_tag.get_text().lower():
                crisis_press_releases.append(curr_url)  # Add the URL to the list of crisis press releases because of title
                print(len(crisis_press_releases))
                crisis_press_release_soup.append(soup)
                
            elif "crisis" in body_div.get_text().lower():
                crisis_press_releases.append(curr_url)  # Add the URL to the list of crisis press releases because of body
                print(len(crisis_press_releases))
                crisis_press_release_soup.append(soup)

        # Find child URLs and add them to the queue if they meet the criteria
        if curr_url.endswith(".doc.htm") == False: # I don't want to extract links from releases as this is not helpful
            for tag in soup.find_all('a', href=True):
                child_url = tag['href']
                child_url = urllib.parse.urljoin(curr_url, child_url)
                if child_url.startswith(seed_url) == True and child_url not in seen: # If we have a new link that begins with the seed add it
                    urls.append(child_url)
                    seen.append(child_url)

    except Exception as ex:
        continue

print("Number of URLs seen = %d, and scanned = %d" % (len(seen), len(opened)))
print("URLs with 'Press Release' anchor tag and the word 'crisis' in title or text:")
for crisis_url in crisis_press_releases:
    print(crisis_url) # Result

# Calculate the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")

# Soup text files
# Iterate through the list
for idx, soup in enumerate(crisis_press_release_soup):
    # Serialize the BeautifulSoup object to a string
    soup_str = str(soup)
    idx = idx + 1

    # Define a filename based on the index
    filename = f"1_{idx}.txt"

    # Write the serialized soup to a text file
    with open(filename, "w", encoding="utf-8") as text_file:
        text_file.write(soup_str)

    print(f"Saved {filename}")

print("Serialization and saving complete.")
