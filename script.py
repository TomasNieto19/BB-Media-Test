from playwright.sync_api import sync_playwright
import requests
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

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {jwt}'
    }
    
    response = requests.get('https://service-vod.clusters.pluto.tv/v4/vod/categories?includeItems=true&offset=1000&page=1', headers=headers)
    
    data = response.json()

    series_category_id = "619043246d03190008131b89"

    movies_category_id = "618da9791add6600071d68b0"

    movies_and_series = []

    for category in data["categories"]:
        if any(main["categoryID"] == series_category_id or main["categoryID"] == movies_category_id for main in category["mainCategories"]):
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
                        "category": category_name
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
                        "category": category_name
                    }
                    movies_and_series.append(series_data)
    
    with open('movies_and_series.json', 'w', encoding='utf-8') as json_file:
        json.dump(movies_and_series, json_file, ensure_ascii=False ,indent=4)



    print(f"Execution time: {time.time() - start_time:.2f} seconds")



if __name__ == "__main__":
    main()
