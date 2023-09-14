from veryfi import Client
import re
import os
import glob
import json

# La idea es iterar a lo largo de cada archivo y generar un JSON para cada uno.
# Algunos de los items que pide la prueba los detecta la API entonces simplemente voy a trabajar con esos.
# Respecto a Line_items, la descripción puede llegar a ser muy ambigua entonces voy a usar la que propone la API. 
# Respecto a la cantidad y el valor, hay que tener en cuenta que no todos los items tienen cantidad, cuando por ejemplo se habla de servicios.
# La cardinalidad de los items en una lista está dada por el valor; es decir, todo tiene un precio pero puede no tener una cantidad. Basado en esto,
# voy a buscar cuantos valores hay y generar un item por cada valor. Para esto voy a usar lo que la API detecta como TEXTO para compararlo con lo que detecta como
# VALOR.

def call_API(File_name):
    client_id = 'vrfKBlY8yHJLIE5usrt1LbPBbZD5EKUTSCsKEiS'
    client_secret = '5vbF0rdc8MZMo7F61lHeiactiiyo9EKCdmgwJxJWFokM9RyDb0iCyvkDoZm5hK7UOWgLUjIEw1WGK40hWjWBEtER9lbvw2UcSN9KVFtecTcEbgiOFSTFxnaRM4CRoiYA'
    username = 'ale585398'
    api_key = '06c7acac591f507bb8a2c4c6a5bc9e47'
    categories = []
    file_path = jpg_file

    # This submits document for processing (takes 3-5 seconds to get response)
    veryfi_client = Client(client_id, client_secret, username, api_key)
    response = veryfi_client.process_document(file_path, categories=categories)
    return response

def detect_begginig_number(text):
    ### Esta función detecta la cantidad basado en el número que comineza el string TEXTO de la API
    ### Solo puede haber un único número al inicio del string,
    ### Por lo que no hay necesidad de considerar múltiples coincidencias
    try:
        match = re.search(r'^\d+(,\d+)?(\.\d+)?',text)
        number = match.group(0)
        return number
    except:
        return None


def detect_number_after_money(text):
    ### Cada precio corresponde a un artículo o a un servicio. Si es un servicio, puede que no tenga cantidad.
    ### Esta función recibe el texto que encontró la API en cada line_item y 
    ### regresa todos los valores que estén precedidos de un $
    try:
        matchs = re.findall(r'\$([\d,]+(?:\.\d+)?)',text)
        return matchs
    except:
        return None


def Value_Description_quantity_array(response):
    ### Esta función construye un diccionario por cada valor usando su descripción y catidad.
    
    list_of_items = []
    for i in response['line_items']:
        try:
            Total_API = i['total']
            Descripcion_API = i['description']
            quantity = detect_begginig_number(i['text'])
            Value = detect_number_after_money(i['text'])
            Value = Value[0].replace(',','')
            Value = float(Value)

            if Total_API == Value: 
                ### La idea es que si la función encontró un valor seguido de '$' en el texto y la APi también encontró ese valor en Value, 
                # tiene que ser el valor de un producto, no algún valor en la descripción.
                line_item_array = {'quantity':quantity, 'Description':Descripcion_API, 'Value': Value}
                list_of_items.append(line_item_array)
            else:
                continue

        except:
            continue

    return list_of_items


current_directory = os.getcwd()
jpg_files = glob.glob(os.path.join(current_directory, "*.jpg"))

JSON_file = {}

for jpg_file in jpg_files:
    response = call_API(jpg_file)
    JSON_file['bill_to_name'] = response['bill_to']['name']
    JSON_file['bill_to'] = response['bill_to']['address']
    JSON_file['ship_to_name'] = response['ship_to']['name']
    JSON_file['ship_to_address'] = response['ship_to']['address']
    List_of_items = Value_Description_quantity_array(response)
    JSON_file['line_items'] = List_of_items
    save_file = open("{}.json".format(jpg_file[-14:-4]), "w")  
    json.dump(JSON_file,save_file, indent=6)
    save_file.close()
    