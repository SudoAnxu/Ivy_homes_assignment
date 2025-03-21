import requests
import time
import logging

# Set up logging to record status
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "http://35.200.185.69:8000/"
API_VERSIONS = ["v1", "v2", "v3"]
DELAY = 2  # Delay in seconds between consecutive requests
MAX_RETRIES = 3  # Maximum number of retries for a request

# Creating a set() to store unique names for each version
all_names = {version: set() for version in API_VERSIONS}

def extract_names(base_url, api_version, prefix="", depth=0, max_depth=2):
    if depth > max_depth:
        return
    # Extraction process for each version
    retries = 0
    while retries <= MAX_RETRIES:
        try:
            response = requests.get(f"{base_url}/{api_version}/autocomplete?query={prefix}")
            response.raise_for_status()  # Raise an exception for HTTP errors
            break
        # Error handling
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logging.warning(f"Rate limit hit. Retrying in {DELAY} seconds...")
                time.sleep(DELAY * (retries + 1))  # Exponential backoff
                retries += 1
            else:
                logging.error(f"Request failed: {e}")
                return
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return
    
    data = response.json()
    results = data.get("results", [])
    
    # Storing and logging extraction status
    for name in results:
        if name not in all_names[api_version]:
            all_names[api_version].add(name)
            logging.info(f"Extracted name from {api_version}: {name}")
            extract_names(base_url, api_version, prefix=name, depth=depth+1, max_depth=max_depth)
    
    # Introduce a delay to avoid rate limiting
    time.sleep(DELAY)

def main():
    logging.info("Starting name extraction process...")
    
    # Start extraction with all letters of the alphabet
    for version in API_VERSIONS:
        print(f"Extracting names from {version}...")
        for letter in "abcdefghijklmnopqrstuvwxyz":
            extract_names(BASE_URL, version, prefix=letter)
        print(f"Total names extracted from {version}: {len(all_names[version])}")
    
    logging.info(f"Total names extracted across all versions: {sum(len(names) for names in all_names.values())}")
    logging.info("Extraction complete.")
    
    # Saving extracted names to a file
    with open("extracted_names_1.txt", "w") as f:
        for name in all_names:
            f.write(name + "\n")

if __name__ == "__main__":
    main()
