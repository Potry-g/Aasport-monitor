from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from threading import Thread
from bs4 import BeautifulSoup
from product_class import Product

glo_var = True
glo_var_stat = False

def get_pruduct_urls(soup,browser):

    urls = []
    cool = True
    while cool:
        try:
            for link in soup.find(class_="products columns-4").find_all(class_="product-item"):
                urls.append(link.find(class_="product-item-link").get("href"))
            cool = False
        except:
            soup = load_urls(browser)
            print("None soup error")

    return urls

def read_file(file_path):

    f = open(file_path, "r")
    file_content = f.readlines()
    f.close()

    return file_content

def write_file(file_path, urls):
    
    f = open(file_path,"w")

    for cool in urls:
        f.write(cool + "\n")

    f.close()

def monitor_urls(file_content, urls):

    sneakers = []

    for i in range(len(urls)):
        if not urls[i] + "\n" in file_content:
            cool = Product(urls[i])
            cool.send_hook()
            sneakers.append(cool)

    return sneakers

def open_browser(url):

    for _ in range(3):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")

            browser = webdriver.Chrome(options=chrome_options)
            browser.get(url)
            print("Browser opened.")
            return browser
        except:
            print("Could not open browser")

    

def load_urls(browser):

    for _ in range(3):
        try:
            browser.switch_to.window(browser.window_handles[0])
            browser.refresh()
            site = browser.page_source
            soup = BeautifulSoup(site, 'html.parser')

            return soup
        except:
            print("could not refresh page")

def take_input():

    global glo_var, glo_var_stat

    cool = ""
    while cool.lower() != "exit":
        cool = input()
        if cool.lower() == "stats":
            glo_var_stat = True

    glo_var = False

def main():

    global glo_var, glo_var_stat

    thr_input = Thread(target=take_input)
    thr_input.start()

    main_url = "https://aasport.ro/adidasi-nike-originali/?swoof=1&post_type=product&woof_text=jordan&product_cat=adidasi"

    file_path = "/home/alex/main/aasport monitor/product_urls.txt"
    file_content = read_file(file_path)
    urls = []
    prd_obj = []
    del_obj = []
    res_time = int(time.time())

    browser = open_browser(main_url)

    while glo_var:
        del_obj = []
        cool = False

        soup = load_urls(browser)
        urls = get_pruduct_urls(soup,browser)

        if glo_var_stat:
            if prd_obj:
                for i in range(len(prd_obj)):
                    print(prd_obj[i].name)
            print(browser.title)
            
            glo_var_stat = False
        
        for url in urls:
            if not url + "\n" in file_content:
                prd = Product(url,browser)
                if prd.stock:
                    prd.send_hook()
                    prd_obj.append(prd)
                cool = True

        if cool:
            write_file(file_path,urls)
            file_content = read_file(file_path)

        if prd_obj:
            for i in range(len(prd_obj)):
                if not prd_obj[i].monitor():
                    del_obj.append(i)

            del_obj = del_obj[::-1]
            for i in del_obj:
                prd_obj[i].dell()
                del prd_obj[i]

        if int(time.time()) - 1200 >= res_time:
            res_time = int(time.time())
            browser.quit()
            browser = open_browser(main_url)

            if prd_obj:
                for i in range(len(prd_obj)):
                    prd_obj[i].browser = browser
                    prd_obj[i].open_new_tab()

    if prd_obj:
        for _ in range(len(prd_obj)):
            prd_obj[0].dell()
            del prd_obj[0]

    browser.quit()


if __name__=="__main__":

    main()