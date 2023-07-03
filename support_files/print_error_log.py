import datetime
import sys

def print_error_log(date):
  if len(sys.argv) > 1:
    print("=" * 30)
    print("Error log for", date)
    print("=" * 30)
    for line in sys.stderr:
      print(line)
  else:
    print("No errors")

if __name__ == "__main__":
  date = datetime.datetime.now().strftime("%Y-%m-%d")
  print_error_log(date)
