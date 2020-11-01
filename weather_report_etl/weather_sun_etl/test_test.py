from datetime import date
import datetime

today = date.today()
tomorrow = today + datetime.timedelta(days=9)
print(str(today))