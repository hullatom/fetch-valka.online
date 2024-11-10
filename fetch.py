#!/bin/python3

#pip install requests beautifulsoup4


import requests # type: ignore
from bs4 import BeautifulSoup  # type: ignore
import re
import os
import csv
from datetime import datetime, timedelta


outputFileCss = "output.css"
outputPage = ''


MainUrl = 'https://valka.online/category/aktualni-konflikty/valka-na-ukrajine-denni-analyzy/'
# Přidání hlavičky User-Agent
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}


def main():

    #hotovat prace
    data_list = getCsv()

    # Výpis odkazů
    links = set()
    #links.update(get_article_links(MainUrl))
    #for i in range(3,10,1):
    #    links.update(get_article_links(f'https://valka.online/category/aktualni-konflikty/valka-na-ukrajine-denni-analyzy/page/{i}/'))

    print(f'pocet linku: {len(links)}')

    for link in links:
        
        link = dict(link)
        date = link['date']

        found = False
        
        #pro kazdy link projedu dict
        for zaznam in data_list:

            zaznDate = zaznam['date']

            if zaznDate == date:

                found = True

                if zaznam['state'] != 'no':
                    continue

                zaznam['state'] = 'link'
                zaznam['link'] = link['href']
                


            continue

        if found == False:
            newZaznam={}
            newZaznam['date'] = link['date']
            newZaznam['state'] = 'link'
            newZaznam['link'] = link['href']
            newZaznam['souhrn'] = ''
            newZaznam['diplomacie'] = ''
            newZaznam['ekonomika'] = ''
            newZaznam['tresnicka'] = ''
            #diplomacie; ekonomika; tresnicka;
            data_list.append(newZaznam)

        continue

    print('sorting csv...')

    # Seřazení podle data
    data_list.sort(key=lambda row: datetime.strptime(row["date"], "%d-%m-%Y"), reverse=True)

    indexFile = 'data/index.html'
    eraseoutputFile(indexFile)
    indexPage = ''
    indexPage = initOutputFile(indexPage, indexFile)

    #Cti clanky
    for zaznam in data_list:

        zaznam['souhrn'] = ''

        #kdy zaznam neni komplet
        if zaznam['state']=='link': #or zaznam['state']=='souhrn':
            soup = ''
            try:
                soup = getPage(zaznam['link'])
            except:
                print(f'skipping...   {zaznam['link']}')
                pass
            
            if soup:
                parsePage(soup, zaznam)
                zaznam['state']='all'


        #pridej do html
        createHTML(zaznam)

        tg = indexPage.new_tag('p')
        tg.append(BeautifulSoup(f'<a href="pages/{zaznam['date']}.html">{zaznam['date']}</a>', "html.parser"))
        indexPage.body.append(tg)

        continue

    setCsv(data_list)
    saveOutputfile(indexPage, indexFile)

    return

def eraseoutputFile(outputFile):

    print(f'erasing {outputFile}...')

    with open(outputFile, 'w', encoding="utf-8"):
        pass  # Soubor je nyní vytvořen, ale není do něj nic napsáno


    return

def initOutputFile(outputPage, outputFile):

    try:
        with open(outputFile, "r") as file:
            all = file.read()
    except:
        #create
        eraseoutputFile(outputFile)
        all=''

    if not all.startswith("<!DOCTYPE html>\n"):
        doctype = "<!DOCTYPE html>\n"
        all = doctype + all
    
    outputPage = BeautifulSoup(all, "html.parser")

    if not outputPage.html:
        html = outputPage.new_tag('html')
        html['lang'] = 'cs'
        outputPage.append(html)
    
    if not outputPage.html.head:
        head = outputPage.new_tag('head')
        outputPage.html.append(head)

    if not outputPage.html.head.meta:
        meta = outputPage.new_tag('meta')
        meta['charset'] = 'utf-8'
        outputPage.html.head.append(meta)

    if not outputPage.html.head.title:
        title = outputPage.new_tag('title')
        title.string = 'hullatom.cz - valka.online výzob'
        outputPage.html.head.append(title)
    
    if not outputPage.html.body:
        body = outputPage.new_tag('body')
        outputPage.html.append(body)

    if not outputPage.html.head.link or outputPage.html.head.link['href']!=outputFileCss:
        link_tag = outputPage.new_tag('link', rel='stylesheet', href=outputFileCss)
        link_tag2 = outputPage.new_tag('link', rel='stylesheet', href=f'../{outputFileCss}')
        outputPage.html.head.append(link_tag)
        outputPage.html.head.append(link_tag2)

    return outputPage

def saveOutputfile(outputPage, outputFile):
    
    #initOutputFile(outputPage, outputFile)
    
    # Uložení změněného HTML zpět do souboru
    with open(outputFile, "w", encoding="utf-8") as file:
        file.write(outputPage.prettify())

def createHTML(zaznam):

    outputPage = outputPage = BeautifulSoup('', "html.parser")
    outputFile = f'data/pages/{zaznam['date']}.html'

    #pokud soubor neni, tak ho vyvori
    outputPage = initOutputFile(outputPage, outputFile)

    #najdi dic class="article {date}"
    article = outputPage.html.body.find('div', class_=lambda x: x and 'article' in x and zaznam['date'] in x)

    date_obj = datetime.strptime(zaznam['date'], '%d-%m-%Y')
    previous_day = date_obj - timedelta(days=1)
    next_day = date_obj + timedelta(days=1)
    previous_day_str = previous_day.strftime('%d-%m-%Y')
    next_day_str = next_day.strftime('%d-%m-%Y')



    #pokud neni, vytvor
    if not article:
        article = outputPage.new_tag('div')
        article['class'] = ['article', zaznam['date']]
        outputPage.html.body.append(article)
        pass

    if not article.find('p', class_='art_links_top'):
        tg = outputPage.new_tag('p')
        tg['class'] = ['art_links_top']
        tg.append(BeautifulSoup(f'<a href="{previous_day_str}.html" style="text-align: left; display: block;">předchozi</a>', "html.parser"))
        tg.append(BeautifulSoup(f'<a href="../index.html" style="text-align: center; display: block;">index</a>', "html.parser"))
        tg.append(BeautifulSoup(f'<a href="{next_day_str}.html" style="text-align: right; display: block;">další</a>', "html.parser"))
        article.append(tg)

    if not article.find('h2', class_='art_title'):
        tg = outputPage.new_tag('h2')
        tg['class'] = ['art_title']
        tg.string = zaznam['date']
        article.append(tg)

    if not article.find('p', class_='art_link'):
        tg = outputPage.new_tag('p')
        tg.append(BeautifulSoup(f'<a href="{zaznam['link']}">{zaznam['link']}</a>', "html.parser"))
        tg['class'] = ['art_link']
        article.append(tg)

    if not article.find('div', class_='diplomacie'):
        diplomacie = outputPage.new_tag('div')
        diplomacie['class'] = ['diplomacie']
        diplomacie.append(BeautifulSoup(zaznam['diplomacie'], "html.parser"))
        article.append(diplomacie)
    
    if not article.find('div', class_='ekonomika'):
        ekonomika = outputPage.new_tag('div')
        ekonomika['class'] = ['ekonomika']
        ekonomika.append(BeautifulSoup(zaznam['ekonomika'], "html.parser"))
        article.append(ekonomika)
    
    if not article.find('div', class_='tresnicka'):
        tresnicka = outputPage.new_tag('div')
        tresnicka['class'] = ['tresnicka']
        tresnicka.append(BeautifulSoup(zaznam['tresnicka'], "html.parser"))
        article.append(tresnicka)

    if not article.find('p', class_='art_links_bottom'):
        tg = outputPage.new_tag('p')
        tg['class'] = ['art_links_bottom']
        tg.append(BeautifulSoup(f'<a href="{previous_day_str}.html" style="text-align: left; display: block;">předchozi</a>', "html.parser"))
        tg.append(BeautifulSoup(f'<a href="../index.html" style="text-align: center; display: block;">index</a>', "html.parser"))
        tg.append(BeautifulSoup(f'<a href="{next_day_str}.html" style="text-align: right; display: block;">další</a>', "html.parser"))
        article.append(tg)

    saveOutputfile(outputPage, outputFile)

    return

def parsePage(soup, zaznam):

    #content = content.replace("\n", "").replace("\r", "").replace(";", ",")

    article = soup.find('div', class_='entry-content')

    diplActive = False
    diplHTML = ''

    ekonomikaActive = False
    ekonomikaHTML = ''

    tresnickaActive = False
    tresnickaHTML = ''
    
    for child in article.children:
        if child.name:

            if child.name != 'p' and child.name != 'hr':
                continue 

            if child.name == 'hr':
                diplActive = False
                ekonomikaActive = False
                tresnickaActive = False
            else:
                strong = child.find('strong')

                if strong and strong.get_text() :

                    text = strong.get_text().strip()

                    if 'Diplomatické a politické události' in text:
                        diplActive = True
                    if 'Svéráz ®uské ekonomiky' in text:
                        ekonomikaActive = True
                    if 'Třešnička™' in text:
                        tresnickaActive = True

            if diplActive == True:
                diplHTML = diplHTML + str(child)
            if ekonomikaActive == True:
                ekonomikaHTML = ekonomikaHTML + str(child)
            if tresnickaActive == True:
                tresnickaHTML = tresnickaHTML + str(child)
        
        continue

    diplHTML = diplHTML.replace("\n", "").replace("\r", "").replace(";", ",")
    ekonomikaHTML = ekonomikaHTML.replace("\n", "").replace("\r", "").replace(";", ",")
    tresnickaHTML = tresnickaHTML.replace("\n", "").replace("\r", "").replace(";", ",")
            
    zaznam['diplomacie'] = diplHTML
    zaznam['ekonomika'] = ekonomikaHTML
    zaznam['tresnicka'] = tresnickaHTML


    return

def parseSouhr(ps):

    if(len(ps)>0):
        return ps[1].prettify()
    return 'souhrn'

def getPage(link):

    return getSoup(link)

    return

def contains_date(string):
    # Regulární výraz pro formát dd-mm-yyyy
    pattern = r"\b\d{2}-\d{2}-\d{4}\b"
    
    # Vyhledání shody s datem
    match = re.search(pattern, string)
    
    if match:
        return match.group()
    else:
        return ''

def getSoup(url):

    print('reading www...')

    # Stáhnout stránku
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()  # Zkontrolovat, zda bylo stažení úspěšné

    print('reading soup...')
    # Analyzovat HTML obsah
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup



    
def get_article_links(url):

    links = set()

    soup = getSoup(url)

    print('reading links...')

    # Najít všechny odkazy na články (úprava podle struktury stránky)
    for a_tag in soup.find_all('a', href=True):

        href=a_tag['href']

        datum =  contains_date(href)
        
        if datum != '':  # Filtr na odkazy na články
            
            obj={
                'date': datum,
                'href': href
            }
            
            links.add(frozenset(obj.items()))    
            pass       
            

    return links


def getCsv():

    print('reading csv...')

    # Načtení CSV souboru do seznamu slovníků
    with open("data/done.csv", mode="r") as file:
        
        csv_reader = csv.DictReader(file, delimiter=";")

        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]
        
        data_dict = [row for row in csv_reader]

        

        return data_dict



def setCsv(data_list):

    fieldnames = data_list[0].keys()

    print('writing csv...')

    # Uložení dat do CSV souboru
    with open("data/done.csv", mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")

        # Zapsání hlavičky (názvů sloupců)
        writer.writeheader()

        # Zapsání jednotlivých řádků
        for row in data_list:
            writer.writerow(row)
    return

main()


