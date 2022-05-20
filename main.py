import pathlib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd

import csv

def scrapWeb(url = ""):

    chrom_opt = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 2, 'plugins': 2,
                                                        'popups': 2, 'geolocation': 2, 'notifications': 2,
                                                        'auto_select_certificate': 2, 'fullscreen': 2,
                                                        'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                        'media_stream_mic': 2, 'media_stream_camera': 2,
                                                        'protocol_handlers': 2, 'ppapi_broker': 2,
                                                        'automatic_downloads': 2, 'midi_sysex': 2,
                                                        'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                        'metro_switch_to_desktop': 2,
                                                        'protected_media_identifier': 2, 'app_banner': 2,
                                                        'site_engagement': 2, 'durable_storage': 2}}
    chrom_opt.add_experimental_option("prefs", prefs)

    #chrom_opt.headless = True
    #chrom_opt.add_argument("--headless")

    # inicialize a new webdriver

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrom_opt)
    driver.get(url)

    arrayReturn = []

    # fields are required: precioMain and navegacion-secundaria__migas-de-pan
    # to find the price and categories respectively
    pricebase = driver.find_elements(by=By.CLASS_NAME, value='precioMain')
    categories = driver.find_elements(by=By.CLASS_NAME, value='navegacion-secundaria__migas-de-pan')
    priceWithoutDiscount = driver.find_elements(by=By.CLASS_NAME, value='original-price-nodiscount')


    if pricebase:

        # Dont interes the father categorie "Home" because is remove
        categories = categories[0].text.replace("Home", "")
        pvp = float(pricebase[0].text.replace("€","").replace(",","."))
        pai = str(round(pvp / 1.21,2)).replace(".",",") + "€"

        arrayReturn.append(pricebase[0].text)
        arrayReturn.append(pai)

        if priceWithoutDiscount:
            arrayReturn.append(priceWithoutDiscount[0].text)
        else:
            arrayReturn.append(0)

        # Give format to categories
        for i in range(len(categories)):
            if (categories[i - 1].islower() is True) and (categories[i].isupper() is True):
                categories = categories[:i] + "/" + categories[i:]
        if categories[0] == "/":
            categories = categories[1:]

        arrayReturn.append(categories.split("/"))

    return arrayReturn



def categoriesFilter(file=""):
    try:
        col_list = ["Categoria", "Utiles"]
        df = pd.read_csv(file, sep=";", usecols=col_list)

        return df
    except Exception as e:
        print("Cant read the file categorias")
        print(e)


def readCSV(file=""):
    try:
        # Create a array with the names of all categories
        col_list = ["Codigo", "Categoria", "Articulo", "PVP SIN IVA", "PVP", "Stock", "Plazo", "P/N", "Eean", "Peso",
                    "Marca/Fabricante", "Canon"]
        # Read the CSV file with ";" as a delimiter and asign the names of the columns
        df = pd.read_csv(file, sep=";", usecols=col_list)

        return df

    except Exception as e:
        print('ERROR- when trying to read CSV file')
        print(e)


def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b)
    return s


def fixNameProducts(fileProducts="", fileCategories=""):
    try:
        df = readCSV(fileProducts)
        productsName = []
        categories = categoriesFilter(fileCategories)
        utilCategories = []

        for category in range(len(categories)):
            if categories["Utiles"][category] == 1:
                utilCategories.append(categories["Categoria"][category])

        for product in range(len(df)):
            if df["Categoria"][product] in utilCategories:
                fixName = str(df["Articulo"][product]).replace(" ", "-").replace("\"", "").replace("'", "").replace(".","").replace("/", "-").replace("+", "")
                fixName = fixName.replace("--", "-").replace("(", "").replace(")", "").replace("ñ", "n")
                productsName.append(normalize(fixName))

        return productsName

    except Exception as e:
        print("ERROR- Cant fix the name of products")
        print(e)


def generateURL(s=""):
    url = "https://www.pccomponentes.com/" + s.lower()

    return url


def createCSV(path = "."):
    file = path + "datosPCBOX.csv"
    path = pathlib.Path(path)

    header = ['Name', 'URL', 'PVP', 'PAI','PVP sin Descuento' 'Category', 'Subcategory1', 'Subcategory2']

    if not path.exists():
        with open(file,'w',encoding="UTF8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

def writeCSV(array,file = ""):
    with open(file, 'w', encoding="UTF8") as f:
        writer = csv.writer(f)
        header = ['Name', 'URL', 'PVP', 'PAI', 'PVP sin Descuento', 'Category', 'Subcategory1', 'Subcategory2']
        writer.writerow(header)

        for row in array:
                writer.writerow(row)

        f.close()

if __name__ == '__main__':

    productsNameFixed = fixNameProducts('./docs/tarifa.csv', './docs/categorias.csv')
    masiveDataArray = []
    for product in range(10):
        dataCSV = []
        dataCSV.append(productsNameFixed[product])
        url = generateURL(productsNameFixed[product])
        dataCSV.append(url)
        dataScrap = scrapWeb(url)
        for data in dataScrap:
            if isinstance(data,list):
                for category in data:
                    dataCSV.append(category)
            else:
                dataCSV.append(data)
        if len(dataCSV) > 4:
            masiveDataArray.append(dataCSV)
            #print(dataCSV)

    createCSV("./docs/")
    writeCSV(masiveDataArray,"./docs/datosPCBOX.csv")




    print(scrapWeb("https://www.pccomponentes.com/xiaomi-redmi-note-11-4-128gb-azul-ocaso-libre"))
    print(scrapWeb("https://www.pccomponentes.com/asus-chromebook-flip-z3400ft-intel-core-m3-8100y-8gb-64gb-emmc-14-tactil"))
