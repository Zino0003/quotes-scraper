import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("quotes_scraper.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

list_of_dicts=[]
url = "http://quotes.toscrape.com"
second_url=""

while second_url is not None:
    try: 
        headers={"User-Agent" : "Mozilla/5.0 (windows NT 10.0; win64; x64) Applewebkit/537.36"}
        response = requests.get(url=url+second_url , timeout=(5,10) , headers=headers)
        response.encoding = "utf-8"                
        response.raise_for_status()
        soup = BeautifulSoup (response.text , "lxml")
        logger.info(f"Scraping: {url+second_url}")
        quotes=soup.find_all("div",class_="quote")
        for quote in quotes:
            name=quote.select_one("small.author")
            if name:
                author_name=name.get_text(strip=True)
            else:
                author_name="Doesn't exist"
            q=quote.select_one("span.text")
            if q:
                author_quote=q.get_text(strip=True)
            else:
                author_quote="Doesn't exist"
            link=quote.select_one("span>a")
            if link:
                author_link=link.get("href","Doesn't exist")
            else:
                author_link="Doesn't exist"
            tags=quote.find_all("a" , class_="tag")
            tags_list=[]
            for tag in tags:
                tag_name=tag.get_text(strip=True)
                tags_list.append(tag_name)

            dictnr={"Author name":author_name , "His quote":author_quote , "Author page link":author_link , "Tags":tags_list}
            list_of_dicts.append(dictnr)

        logger.debug(f"The page {url+second_url} has scraped")

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        break   
    except requests.exceptions.Timeout:
        logger.error("Server response delay — please try again")
        break
    except requests.exceptions.ConnectionError:
        logger.error("Internet outage or server not available")
        break
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        break
    except Exception as e : 
        logger.error(f"Error found: {e}")
        break
    
    else:
        next_page_link=soup.select_one("li.next>a")
        if next_page_link:
            second_url=next_page_link.get("href")
        else:
            second_url=None
            logger.debug("The scraping finished")
    
    
# print(list_of_dicts)
logger.info(f"Number of quotes in the website: {len(list_of_dicts)}")

df = pd.DataFrame(list_of_dicts)
# print(df)
# df.info()
# print(df.sample(8))
# print(f"Type of each column: {df.dtypes}")
# print(f"The number of different quotes: {df['His quote'].nunique()}")
# print(f"Number of empty cells in each column: {df.isnull().sum()}")
df["Tags"] = df["Tags"].apply(lambda tags: ", ".join(tags))  #Transfering Tags column elements from list to str
df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
logger.debug(f"Some lines of the final data form: {df.sample(8)}")
df.to_csv("Quotes_scraping.csv" , index=False , encoding="utf-8-sig")
logger.info("The process of extracting and cleaning the data from the website has been completed. You can view the results in the csv file.")

