from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import slack_sdk
from datetime import datetime
from tabulate import tabulate
import re

# Create a bot in advance from the slack
slack_token = 'xoxb-5570734011559-5625437831972-xlHwW1xQteOrsunQmxKs6flp'
client = slack_sdk.WebClient(token=slack_token)

# send today's date
dt = datetime.today().strftime('%Y-%m-%d')
client.chat_postMessage(channel= 'Your_Channel_Name', text =f'''{dt} I'm going to buy the lottery ticket''') # write the name of your slack channel name in 'Your_Channel_Name'

url = 'https://dhlottery.co.kr/user.do?method=login&returnUrl='
driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="114.0.5735.90").install()))
driver.get(url)

time.sleep(1)

# login
driver.find_element(By.XPATH, value = '//*[@id="userId"]').send_keys('Your_ID') # write the ID of https://dhlottery.co.kr/common.do?method=main
time.sleep(0.5)
driver.find_element(By.XPATH, value = '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/input[2]').send_keys('Your_Password') #  write the password of https://dhlottery.co.kr/common.do?method=main
time.sleep(0.5)
driver.find_element(By.XPATH, value = '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/a').click()
time.sleep(1)

# send a previus result
driver.get('https://dhlottery.co.kr/userSsl.do?method=myPage')
driver.find_element(By.XPATH, value = '//*[@id="article"]/div[2]/div/div[2]/div/a').click()
time.sleep(0.5)
driver.find_element(By.XPATH, value = '//*[@id="frm"]/table/tbody/tr[3]/td/span[2]/a[2]').click()
driver.find_element(By.XPATH, value = '//*[@id="submit_btn"]').click()
time.sleep(1)

# reulst table
iframe = driver.find_element(By.XPATH, value = '//*[@id="lottoBuyList"]')
driver.switch_to.frame(iframe)
tbl = driver.find_element(By.XPATH, value='/html/body/table') # Error when you trying to access the table right away. Because it is in iframe, it acts as if it is loading another web page

tbl_list = []
table_tr = tbl.find_elements(By.TAG_NAME, 'tr')
tbl_list.append([i.text for i in table_tr[0].find_elements(By.TAG_NAME, 'th')])

for a in range(1, len(table_tr)):
    tbl_list.append([i.text for i in table_tr[a].find_elements(By.TAG_NAME, 'td')])

tbl_results = tabulate(tbl_list, tablefmt = 'grid')

# send as comment
channel_id = client.conversations_history(channel='C05GSMM9Y0P')
messages = channel_id.data['messages']
messages_ts = messages[0]['ts']

client.chat_postMessage(channel = '#Your_Channel_Name', # write the name of your slack channel name in 'Your_Channel_Name'
                        text = tbl_results,
                        thread_ts= messages_ts)

driver.switch_to.default_content() # escape iframe

# check the balance
money = driver.find_element(By.XPATH, value ='/html/body/div[1]/header/div[2]/div[2]/form/div/ul[1]/li[2]/a[1]/strong').text

client.chat_postMessage(channel = '#Your_Channel_Name', # write the name of your slack channel name in 'Your_Channel_Name'
                        text = f'''Your current balance is {money}''',
                        thread_ts= messages_ts)

# If the balance is less than 5,000 won, send a message to charge 30,000 won
if int(''.join(re.findall('\d+', money))) <= 5000:
    driver.find_element(By.XPATH, value='/html/body/div[1]/header/div[2]/div[2]/form/div/ul[1]/li[2]/a[2]').click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, value = '//*[@id="Amt"]/option[4]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, value = '//*[@id="btn2"]/button').click()
    time.sleep(1)

    account = driver.find_element(By.XPATH, value = '//*[@id="contents]/table/tbody/tr[4]/td/span').text
    cost = driver.find_element(By.XPATH, value = '//*[@id="contents"]/table/tbody/tr[2]/td').text

    client.chat_postMessage(channel = '#Your_Channel_Name', # write the name of your slack channel name in 'Your_Channel_Name'
                        text = f'''{account} / {cost} 입급하세요''',
                        thread_ts= messages_ts)

time.sleep(1)

# buying a lottery
try:
    driver.get('https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40')
    iframe = driver.find_element(By.XPATH, value = '//*[@id="ifrm_tab"]')
    driver.switch_to.frame(iframe)
    driver.find_element(By.XPATH, value = '//*[@id="checkNumGroup"]/div[1]/label/span').click()
    time.sleep(1)
    driver.find_element(By.XPATH, value = '//*[@id="amoundApply"]/option[2]').click() # 2장 구매
    time.sleep(1)
    driver.find_element(By.XPATH, value='//*[@id="btnSelectNum"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, value = '//*[@id="btnBuy"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, value = '//*[@id="popupLayerConfirm"]/div/div[2]/input[1]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, value = '//*[@id="closeLayer"]').click()
    time.sleep(1)

    text = "Your purchase has been completed."
except:
    text = 'You've filled all the purchase limits for this week.'

client.chat_postMessage(channel = '#Your_Channel_Name', # write the name of your slack channel name in 'Your_Channel_Name'
                        text = text,
                        thread_ts= messages_ts)

# Balance after purchase completed
driver.get('https://dhlottery.co.kr/common.do?method=main')
money2 = driver.find_element(By.XPATH, value = '/html/body/div[1]/header/div[2]/div[2]/form/div/ul[1]/li[2]/a[1]/strong').text

client.chat_postMessage(channel = '#Your_Channel_Name', # write the name of your slack channel name in 'Your_Channel_Name'
                        text = f'''The remaining balance is {money2}''',
                        thread_ts= messages_ts)

driver.quit()
