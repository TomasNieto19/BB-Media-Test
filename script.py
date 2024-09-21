from playwright.sync_api import sync_playwright

def main():
    url = "https://pluto.tv"
    
    try:
         with sync_playwright() as p:

            browser = p.firefox.launch(headless=False)

            page = browser.new_page()

            page.goto(url)

            page.wait_for_timeout(5000)

            page.click('a[href="/on-demand"]')

            page.wait_for_timeout(5000)

            page.click('span:text("Películas")')

            page.wait_for_timeout(6000)

            
            page.click('a:text("View All")')

            page.wait_for_timeout(5000)


            lis = page.query_selector_all('li')

            data = []

            print(lis)
            for li in lis:
                a_tag = li.query_selector('a')
                if a_tag:
                    href = a_tag.get_attribute('href')
                    print(href)

            print(data)

            page.wait_for_timeout(5000)

            # Cerrar la página
            page.close()

            # Cerrar el navegador
            browser.close()
        
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
