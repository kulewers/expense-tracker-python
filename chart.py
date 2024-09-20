from matplotlib import pyplot as plt
import pandas as pd

from database import engine

from datetime import date, timedelta
import argparse
import calendar


parser = argparse.ArgumentParser(description="Crate a chart of your week's expenses")
parser.add_argument("-o", "--output", required=False, type=str)
args = parser.parse_args()


def main():
  # Load data to appropriate format
  df = pd.read_sql(sql='SELECT id, category, date, amount FROM expense', con=engine, index_col='id')
  df = df.pivot_table(index='date', columns='category', values='amount', aggfunc='sum', fill_value=0)

  # Fill empty dates
  monday = date.today()-timedelta(days=date.today().weekday())
  daterange = pd.date_range(start=monday, periods=7, freq='D', inclusive='both', normalize=True)
  week = [str(t.to_pydatetime().date()) for t in daterange]
  df = df.reindex(week, fill_value=0)

  # Create and style chart
  ax = df.plot(kind='bar', stacked=True, title="Your expenses this week", xlabel='Day', ylabel='Expenses')
  weekdays = list(calendar.day_name) 
  ax.set_xticklabels(weekdays)
  plt.xticks(rotation=20)

  if args.output:
    plt.savefig(f"{args.output}.png")
  else:
    plt.show()


if __name__ == '__main__':
  main()