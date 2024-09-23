from playwright.sync_api import sync_playwright
from utils import custom_request, passage_data_to_json
import json
import time

def main():
    start_time = time.time()

    url = "https://pluto.tv"

    session_response = {}

    try:
         with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)

            page = browser.new_page()

            def handle_response(response):
                if response.url.startswith("https://boot.pluto.tv/v4/start") and response.status == 200:
                    session_response['body'] = response.body()

            page.on('response', handle_response)

            page.goto(url)

            page.wait_for_timeout(1000)

            page.close()

            browser.close()
        
    except Exception as e:
        print(e)

    json_data = json.loads(session_response['body'])

    jwt = json_data['sessionToken']

    ## MOVIES AND SERIES REQUEST

    movies_and_series_data = custom_request('https://service-vod.clusters.pluto.tv/v4/vod/categories?includeItems=true', jwt)

    series_category_id = "619043246d03190008131b89"

    movies_category_id = "618da9791add6600071d68b0"

    category_ids = {series_category_id, movies_category_id}

    base_url = "https://pluto.tv/latam/on-demand"

    movies_and_series = []

    for category in movies_and_series_data["categories"]:
        if any(main["categoryID"] in category_ids for main in category["mainCategories"]):
            category_name = category["name"]
            
            for item in category["items"]:
                if item["type"] == "movie":
                    movie_data = {
                        "id": item["_id"],
                        "name": item["name"],
                        "description": item["description"],
                        "duration": item["duration"],
                        "genere": item["genre"],
                        "type": item["type"],
                        "category": category_name,
                        "link": base_url + "/movies/" + item["_id"] + "/details",
                    }
                    movies_and_series.append(movie_data)
                
                elif item["type"] == "series":
                    series_data = {
                        "id": item["_id"],
                        "name": item["name"],
                        "description": item["description"],
                        "genre": item["genre"],
                        "type": item["type"],
                        "seasonsNumbers": item["seasonsNumbers"],
                        "category": category_name,
                        "link": base_url + "/series/" + item["_id"] + "/season/" + str(item["seasonsNumbers"][0]),
                    }
                    movies_and_series.append(series_data)
    
    passage_data_to_json('movies_and_series.json', movies_and_series)

    ## CHANNELS REQUEST LiveTV

    channels_data = custom_request('https://service-channels.clusters.pluto.tv/v2/guide/channels', jwt)

    channels = []

    for channel in channels_data['data']:
        channels.append({
            "id": channel['id'],
            "name": channel['name'],
            "number": channel['number'],
            "summary": channel['summary'],
        })

    passage_data_to_json('channels.json', channels)

    print(f"Execution time: {time.time() - start_time:.2f} seconds") 

if __name__ == "__main__":
    main()
