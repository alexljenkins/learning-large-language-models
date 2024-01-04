from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from dotenv import load_dotenv
load_dotenv()

def get_blog_urls(base_url):
    urls = []
    driver = Chrome()
    driver.get(base_url)

    while True:
        # hit load more until all blogs are loaded
        load_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'loadMoreBlog'))
        )
        driver.execute_script("arguments[0].click();", load_more_button)
        print('loading more blogs...')
        sleep(10)
        if not load_more_button.is_displayed():
            print('finished loading all blogs.')
            break


    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print('Page loaded, starting blog url extraction...')
    for div in soup.find_all('div', class_='post_tile single_item md_item element_anim'):
        link = div.find('a', class_='pt_wrap', href=True)
        if link:
            urls.append(link['href'])
            print(f'link {len(urls)} added: {link["href"]}')
    print(f'found {len(urls)} urls')
    driver.quit()
    return urls

def save_urls(urls):
    with open('datasets/steps_data/blog_urls.txt', 'w') as f:
        f.write('\n'.join(urls))

# from .env just to hide url
urls = get_blog_urls(STEPS_URL)

save_urls(urls)
print(urls)
