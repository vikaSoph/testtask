import requests
import gspread
from datetime import datetime, timedelta
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

# Проблеми коду: 
# - В таблицю вносяться всі запити по датам, курс може дублюватися на одну і ту ж дату, немає фільтрації дат чи їх сортування
# - Залежність програми від формату введення дати користувачем, незручність використання
# - Відсутність перевірки адекватності дати (занадто стара чи дата з майбутнього)
# - При вказанні періоду дат програма працює повільно, при вказані великого проміжку повільно працюватиме 
# - Код працює в консолі, а не розвернуто повноцінною програмою
# - Даний код не "дружить" з аналітикою, він просто записує курси в якісь дати в таблицю та ніяк не використовуються вони в подальшому

# Функція запит курсу USD за вказану дату date_in
def get_currency_rate(date_in):
    url = "https://api.privatbank.ua/p24api/exchange_rates?date=" + date_in
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()
      currency_data = data['exchangeRate']
      for currency in currency_data:
          if currency['currency'] == 'USD':
              return currency['purchaseRate']  
    
    return None

# Функція для визначення курсу USD у вказаний період дат date_from - date_to
def get_more_rate(date_from, date_to):
    current_date = date_from
    while current_date <= date_to:
      currency_rate = get_currency_rate(current_date)
      if currency_rate is not None:
        update_google_sheets(current_date, currency_rate)
      else:
        print("Не вдалося отримати курс валют.")
      current_date = (datetime.strptime(current_date, "%d.%m.%Y") + timedelta(days=1)).strftime("%d.%m.%Y")
  
# Функція запису даних про курс в Google Sheets
def update_google_sheets(date, currency_rate):
  spreadsheet_name = "курс валют ТЗ"
  worksheet_name = "курс"

  scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
  creds = ServiceAccountCredentials.from_json_keyfile_name("exchangerate-402607-c3c303bca7fc.json", scope)
  client = gspread.authorize(creds)

  try:
      spreadsheet = client.open(spreadsheet_name)
      worksheet = spreadsheet.worksheet(worksheet_name)

      row = len(worksheet.get_all_records()) + 2  

      worksheet.update_cell(row, 1, date)
      worksheet.update_cell(row, 2, currency_rate)

      print("Дані успішно оновлені в Google Sheets!")
  except Exception as e:
      print(f"Помилка при записі даних в Google Sheets: {str(e)}")

# Головна функція
def main():
  # Циклічна програма, щоб внести дані багаторазово
  while True: 
    #Якщо обрати ні, то буде здійснено запис для поточної дати
    print ('Необхідно вказати дату? 1 - так, 2 - ні')
    q = input()
    if q == "1":
      print ('Оберіть тип дати: 1 - одинична дата, 2 - період від - до')
      q2 = input()
      if q2 == "1":
        date_in = input('Введіть дату в форматі дд.мм.рррр: ')
        currency_rate = get_currency_rate(date_in)
        if currency_rate is not None:
          update_google_sheets(date_in, currency_rate)
        else:
          print("Не вдалося отримати курс валют.")
      else: 
          date_from = input('Введіть дату початку в форматі дд.мм.рррр: ')
          date_to = input('Введіть дату кінця в форматі дд.мм.рррр: ')
          get_more_rate(date_from, date_to)
    else:
      date_in = date.today().strftime('%d.%m.%Y')
      currency_rate = get_currency_rate(date_in)
      if currency_rate is not None:
        print(f"Курс USD: {currency_rate}")
        update_google_sheets(date_in, currency_rate)
      else:
        print("Не вдалося отримати курс валют.")
    
if __name__ == "__main__":
    main()

