from playwright.sync_api import sync_playwright
from utils import custom_request, passage_data_to_json
import json
import time

def main():
    start_time = time.time()

    url = "https://pluto.tv"

    session_response = {}

    live_tv_content_guide = {}

    channels = {}

    series_category_id = ""

    movies_category_id = ""

    try:
         with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)

            page = browser.new_page()

            def handle_response(response):
                if response.url.startswith("https://boot.pluto.tv/v4/start") and response.status == 200:
                    session_response['body'] = json.loads(response.body().decode('utf-8'))

                if response.url.startswith("https://service-channels.clusters.pluto.tv/v2/guide/timelines") and response.status == 200:
                    live_tv_content_guide['body'] = json.loads(response.body().decode('utf-8'))

                if response.url.startswith("https://service-channels.clusters.pluto.tv/v2/guide/channels") and response.status == 200:
                    channels['body'] = json.loads(response.body().decode('utf-8'))

            page.on('response', handle_response)

            page.goto(url)

            page.wait_for_selector('a[href="/on-demand"]')
            page.click('a[href="/on-demand"]')

            page.wait_for_selector('span:text("Películas")')
            page.click('span:text("Películas")')

            page.wait_for_selector('h3:text("Películas")')
            movies_category_id = page.url.split("on-demand/")[1].split("?")[0]

            page.wait_for_selector('span:text("Series")')
            page.click('span:text("Series")')

            page.wait_for_selector('h3:text("Series")')
            series_category_id = page.url.split("on-demand/")[1].split("?")[0]

            page.close()

            browser.close()
        
    except Exception as e:
        print(e)


    ## MOVIES AND SERIES REQUEST
    movies_and_series_data = custom_request('https://service-vod.clusters.pluto.tv/v4/vod/categories?includeItems=true', session_response['body'].get('sessionToken'))

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


    ## CHANNELS LiveTV
    channels_result = []

    try:
        for channel in channels['body'].get('data', []):
            channels_result.append({
                "id": channel['id'],
                "name": channel['name'],
                "number": channel['number'],
                "summary": channel['summary'],
            })
    except Exception as e:
        print(e)

    passage_data_to_json('channels.json', channels_result)


    # LIVE TV CONTENT GUIDE
    live_tv_content_guide_result = []
    
    try:
        for item in live_tv_content_guide['body'].get('data', []):
            for timeline in item.get('timelines', []):
                timeline_data = {
                    "id": timeline['_id'],
                    "title": timeline['title'],
                    "start": timeline['start'],
                    "stop": timeline['stop'],
                }
                live_tv_content_guide_result.append(timeline_data)
    except Exception as e:
        print(e)

    passage_data_to_json('live_tv_content_guide.json', live_tv_content_guide_result)

    print(f"Execution time: {time.time() - start_time:.2f} seconds")
    # En consola: Execution time: 10.23 seconds

if __name__ == "__main__":
    main()
