import argparse
from datetime import datetime, timedelta

p = argparse.ArgumentParser()
p.add_argument("--begin-date", required=True, type=str)
p.add_argument("--num-dates", required=True, type=int)
a = p.parse_args()

f = "%Y/%m/%d"
b = datetime.strptime(a.begin_date, f)


dates = [(b + timedelta(d)).strftime(f) for d in range(a.num_dates)]
ret = " > ".join([f"type:{date} > return > ctrl+tab" for date in dates])
print(f'python3 keystrokes.py "{ret}" -r 1 -d 0.1')
