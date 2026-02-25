import requests
import json
import os
import sys

# Small script that uses the URL list provided "decodeurURL.json" to verify the URL for each sample
# The accessibility of each file will be printed to the console, and any errors will be listed at the end.
def main():
    if not os.path.exists('decodeurURL.json'):
        print("decodeurURL.json file not found")
        sys.exit(1)

    with open('decodeurURL.json') as json_file:
        url_dict = json.load(json_file)
    error_list=[]
    for decodeur_id, urls in url_dict.items():
        for url_type, url in urls.items():
            try:
                response=requests.get(url, stream=True)
                if response.status_code == 403 or response.status_code == 404:
                    error_list.append(f"{decodeur_id}:{url_type}: HTTP {response.status_code}")
                    print(f"Error accessing {url_type} for {decodeur_id}: HTTP {response.status_code}")
                else:
                    print(f"{url_type} for {decodeur_id} is accessible: HTTP {response.status_code}    ")
                    
            except requests.RequestException as e:
                print(f"Error checking {url_type}: {e}")
    if len(error_list) == 0:
        print("All links verified")
    else:
        print("Some links could not be verified:")
        for error in error_list:
            print(error)

if __name__ == "__main__":
    main()