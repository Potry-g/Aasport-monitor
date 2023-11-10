import ast
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from discord_webhook import DiscordEmbed,DiscordWebhook

class Product:

    def __init__(self, url, browser):

        self.soup = None
        self.min = int(time.time())
        self.url = url
        self.response = None
        self.browser_tab = None
        self.browser = browser

        self.open_new_tab()
        self.update()

    def dell(self):

        self.browser.switch_to.window(self.browser_tab)
        self.browser.close()

        if not self.stock and self.response != None:

            url = "" #Webhook discord

            emb = {
                "title":self.name,
                "url":self.url,
                "color":"0"
            }

            webhook = DiscordWebhook(url=url, username="aasport monitor")
            embed = DiscordEmbed(**emb)
            embed.set_thumbnail(url=self.img_url)
            embed.add_embed_field(name="__OUT OF STOCK__", value="‏‏‎ ‎")
            webhook.add_embed(embed)
            a = webhook.edit(self.response)

            print("oot obj updated: ")
            print(a)


        print(self.name + " object deleted.")

    def in_stock(self):
        
        self.stock = False
        found = self.soup.find(class_="quantity")

        if found != None:
            self.stock = True
        else:
            self.stock = False

    def search_name(self):
        
        self.name = ""
        self.cod_prd = ""

        self.name = self.soup.find(class_="product_title entry-title").string
        self.cod_prd = self.soup.find(class_="sku").text
        
        if self.cod_prd != "Nu se aplică":
            self.name = self.name.replace(self.cod_prd, "")
            while not self.name[len(self.name)-1].isalpha():
                self.name = self.name[:-1]

    def search_img(self):
        
        self.img_url = ""

        for link in self.soup.find_all("img"):
            img_url = link.get("data-large_image")
            if img_url != None:
                self.img_url = "https:" + img_url
                break
    
    def search_price(self):

        self.price = ""

        plm = self.soup.find(class_="summary entry-summary").find(class_="price").find("ins")

        if  plm != None:
            self.price = plm.find(class_="woocommerce-Price-amount amount").text
        else:
            self.price = self.soup.find(class_="woocommerce-Price-amount amount").text

    def search_size_id(self):

        self.size = []
        self.id = []

        dic = self.soup.find(class_="ivpa-register ivpa_registered").get("data-variations")

        for i in range(len(dic)):
            if dic[i] == 't' and dic[i-1] == ':':
                dic= dic[:i] + 'T' + dic[i+1:]

        dic = ast.literal_eval(dic)

        for i in dic:
            self.id.append(i["variation_id"])
            cool = i["attributes"]["attribute_pa_marime-incaltaminte"]
            if len(cool) == 5:
                cool = cool[:4]+"/"+cool[4:]
                self.size.append(cool.replace("-"," "))
            else:
                self.size.append(cool.replace("-","."))

    def make_addtocart_url(self):

        prd_id = self.soup.find(class_="variations_form cart").get("data-product_id")
        cool = []

        for i in range(len(self.size)):
            if self.size[i] == "355":
                self.size[i] = "35.5"
            cool.append(f"[{self.size[i]}](https://aasport.ro/adidasi-nike-originali/cos/?add-to-cart={prd_id}&variation_id={self.id[i]}) | ")

        len_size = len(cool)

        if len_size > 4:
            self.size = ["",""]
            first = int(len_size / 2) + len_size % 2

            for i in range(len_size):
                if i < first:
                    self.size[0] += cool[i]
                else:
                    self.size[1] += cool[i]
                
            self.size[0] = self.size[0][:-2]
            self.size[1] = self.size[1][:-2]

        else:
            self.size = ""

            for i in cool:
                self.size += i

            self.size = self.size[:-2]

    def update(self):

        self.browser.switch_to.window(self.browser_tab)
        self.browser.get(self.url)
        site = self.browser.page_source
        self.soup = BeautifulSoup(site, 'html.parser')

        self.in_stock()
        if not self.stock:
            print("Product out of stock.")
            self.search_img()
            self.search_name()
            return False
        else:
            self.search_name()
            self.search_price()
            self.search_img()
            self.search_size_id()
            self.make_addtocart_url()
            return True
    
    def send_hook(self):

        hoooks ={ 
            "url": "" #Webhook discord,
            "username":"aasport monitor"
        }

        emb = {
            "title":self.name,
            "url":self.url,
            "color":"0"
        }
        if self.cod_prd != "Nu se aplică":
            emb["description"] = "Code: " + self.cod_prd

        Utilities = "[HOMEPAGE](https://aasport.ro/adidasi-nike-originali/)\n"\
                    "[CART](https://aasport.ro/adidasi-nike-originali/cos/)\n"\
                    "[CHECKOUT](https://aasport.ro/adidasi-nike-originali/finalizare-comanda/)\n"

        webhook = DiscordWebhook(**hoooks)
        embed = DiscordEmbed(**emb)
        embed.set_thumbnail(url=self.img_url)

        if type(self.size) is str:
            embed.add_embed_field(name="__Sizes__", value=self.size)
            embed.add_embed_field(name="__Price__", value=self.price)

        else:
            embed.add_embed_field(name="__Sizes__", value=self.size[0])
            embed.add_embed_field(name="__Sizes__‎", value=self.size[1], inline=False)
            embed.add_embed_field(name="__Price__", value=self.price)

        embed.add_embed_field(name="__Utilities__", value=Utilities, inline=False)
        embed.set_footer(text="Written by Potry#3747")
        embed.set_timestamp()
        webhook.add_embed(embed)

        if self.response == None: 
            self.response = webhook.execute()
            print(self.name +" sent to webhook:")
            print(self.response)

        else:
            yes = webhook.edit(self.response)
            print(self.name +" resent webhook:")
            print(yes)

        time.sleep(1)

    def open_new_tab(self):

        self.browser.execute_script("window.open('');")
        self.browser_tab = self.browser.window_handles[len(self.browser.window_handles)-1]

    def monitor(self):

        sec = 900
        
        if self.min > int(time.time()) - sec:
            old_size = self.size
            if self.update():
                if old_size != self.size:
                    self.send_hook()
                    print(self.name + " object updated")
                return True
            else:
                return False
        else:
            return False
        
