import argparse
from datetime import datetime, timedelta

p = argparse.ArgumentParser()
p.add_argument("--begin-date", required=True)
p.add_argument("--end-date", required=True)
a = p.parse_args()

f = "%Y/%m/%d"
b, e = datetime.strptime(a.begin_date, f), datetime.strptime(a.end_date, f)


dates = [(b + timedelta(d)).strftime(f) for d in range((e - b).days + 1)]
ret = " > ".join([f"type:{date} > return > ctrl+tab" for date in dates])
print(f'python3 keystrokes.py "{ret}" -r 1 -d 0.3')
