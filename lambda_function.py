from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from time import sleep
# import os
from webdriver_manager.chrome  import ChromeDriverManager

#  Función para realizar acciones en el navegador
def accion_driver(driver, accion, identificador, etiqueta,keys='-' , tiempo_espera=0.1):
    # driver (WebDriver): La instancia del navegador web.
    # identificador (str): El tipo de identificador, por ejemplo, 'ID', 'XPATH', 'CSS_SELECTOR', etc.
    # etiqueta (str): La etiqueta del identificador (por ejemplo, el ID, la expresión XPath o el selector CSS).
    # accion (str): La acción a realizar ('click' o 'send_keys').
    # keys (str): El texto a introducir en el elemnto
    # tiempo_espera (int): El tiempo de espera en segundos (opcional, por defecto es 1 segundo).
    try:
        if identificador == 'ID':
            elemento = WebDriverWait(driver, tiempo_espera).until(EC.presence_of_element_located((By.ID, etiqueta)))
        elif identificador == 'XPATH':
            elemento = WebDriverWait(driver, tiempo_espera).until(EC.presence_of_element_located((By.XPATH, etiqueta)))
        elif identificador == 'CSS_SELECTOR':
            elemento = WebDriverWait(driver, tiempo_espera).until(EC.presence_of_element_located((By.CSS_SELECTOR, etiqueta)))
        else:
            raise ValueError(f'Tipo de identificador no válido: {identificador}')
        if accion == 'click':
            elemento.click()
        elif accion == 'send_keys':
            elemento.send_keys(keys)
        elif accion == 'clear':
            elemento.clear()
        else:
            raise ValueError(f'Acción no válida: {accion}')
        # Acción completada exitosamente
        return True
    except Exception as e:
        # print(f'Error al realizar la acción {accion}, {etiqueta}: {e}')
        # Error ejecutando acción
        return False
    
class botDian:
    def __init__(self):
        options = webdriver.ChromeOptions()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        # options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--allow-running-insecure-content')
        # main_path = str(os.path.dirname(os.path.abspath(__file__)))
        # chrome_driver_path = os.path.join(main_path,"chrome","chromedriver.exe")
        # service = Service(executable_path=chrome_driver_path)
        # self.driver = webdriver.Chrome(service=service, options=options)
        self.driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    
    def obtainData(self, id):
        driver = self.driver
        try:
            driver.get("https://catalogo-vpfe.dian.gov.co/User/SearchDocument")

            # *************
            try:
                element1 = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/a[1]')
                element2 = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/a[2]')
                ActionChains(driver).move_to_element(element1).move_to_element(element2).perform()
            except:
                pass
            # *************
            accion_driver(driver,'click','XPATH','//*[@id="DocumentKey"]')
            accion_driver(driver,'send_keys','XPATH','//*[@id="DocumentKey"]',str(id))
            sleep(1)
            accion_driver(driver,'click','XPATH','//*[@id="search-document-form"]/button')
            sleep(2)
            try:
                alert = driver.find_element(By.XPATH,'//*[@id="search-document-form"]/div/span').text
                if('Recaptcha inválido' in alert):
                    # Intentar consultar de nuevo
                    flag = 0
                    for i in range(5):
                        try:
                            print(f'Intento: {i}')
                            accion_driver(driver,'click','XPATH','//*[@id="search-document-form"]/button')
                            sleep(1)
                            sellerData = driver.find_element(By.XPATH,'//*[@id="html-gdoc"]/div[3]/div/div[2]/div[1]/p').text 
                            flag = 1
                            break
                        except Exception as e:
                            try:
                                alert = driver.find_element(By.XPATH,'//*[@id="search-document-form"]/div/span').text
                                if 'no encontrado en los registros' in alert:
                                    return {id: 'not found'}
                            except:
                                sleep(1)
                    if flag == 0:
                        return {id: 'captcha error'}
                elif 'no encontrado en los registros' in alert:
                    return {id: 'not found'}
            except Exception as e:
                # print(f'Error: {e}')
                pass
            # Extraer información
            sellerData = driver.find_element(By.XPATH,'//*[@id="html-gdoc"]/div[3]/div/div[2]/div[1]/p').text 
            receiverData = driver.find_element(By.XPATH,'//*[@id="html-gdoc"]/div[3]/div/div[2]/div[2]/p').text
            linkGraphicRepresentation = driver.current_url
            driver.quit()
            # Organizar información
            sellerLines = sellerData.split('\n')
            for line in sellerLines:
                if 'NIT:' in line:
                    sellerDocument = line.split('NIT:')[1].strip()
                elif 'Nombre:' in line:
                    sellerName = line.split('Nombre:')[1].strip()
            receiverLines = receiverData.split('\n')
            for line in receiverLines:
                if 'NIT:' in line:
                    receiverDocument = line.split('NIT:')[1].strip()
                elif 'Nombre:' in line:
                    receiverName = line.split('Nombre:')[1].strip()
            data = {
                'events':[],
                'sellerInformation' : {'document': sellerDocument, 'name': sellerName },
                'receiverInformation' : {'document': receiverDocument, 'name': receiverName },
                'linkGraphicRepresentation' : linkGraphicRepresentation
            }
            return{id : data}
        except Exception as e:
            driver.quit()
            return {id: 'error'}

#Función completa
# 1. Crear instancia
bot = botDian()
# 2. Abrir y minar pagina web
data =  bot.obtainData(id='a907c83fa0bd92871b6257d451edda61ae05c354108be719f9bd2ef6181c945f999d04d61bf91d65d4a48b21577fa4d4')
# 3. Presentación de data
print(data)

def lambda_handler(event, context):
    if 'url' in event:
        url = event['url']
        #Función completa
        # 1. Crear instancia
        bot = botDian()
        # 2. Abrir y minar pagina web
        data =  bot.obtainData(id='a907c83fa0bd92871b6257d451edda61ae05c354108be719f9bd2ef6181c945f999d04d61bf91d65d4a48b21577fa4d4')
        # 3. Presentación de data
        return data
    else:
        return {
            'error': 'Missing url parameter in the event'
        }
