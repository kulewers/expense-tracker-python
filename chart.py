from sqlalchemy.orm import Session
import numpy as np
from matplotlib import pyplot as plt
from datetime import date
import datetime
from database import engine
import models
import argparse


parser = argparse.ArgumentParser(description="Crate a chart of your week's expenses")
parser.add_argument("-o", "--output", required=False, type=str)
args = parser.parse_args()


def main():
  weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

  # Create list of days in current week
  week = [date.today()+datetime.timedelta(days=i-date.today().weekday()) for i in range(7)]

  # Create dictionary of form
  # dict[<category>] == array([<mon>, <tue>, <wed>...])
  with Session(engine) as session:
    weight_counts = {}
    # for each category
    for entry in session.query(models.Expense).group_by(models.Expense.category).distinct():
      category = entry.category
      # initiate array with values for each weekday
      weight_counts[str(category)] = np.zeros(7)
    for idx, day in enumerate(week):
      day_expenses = session.query(models.Expense).filter(models.Expense.date == day).all()
      for expense in day_expenses:
        weight_counts[expense.category][idx] += expense.amount 

  width = .8
  _, ax = plt.subplots(figsize=(10, 7))
  bottom = np.zeros(7)

  for boolean, weight_count in weight_counts.items():
    ax.bar(weekdays, weight_count, width, label=boolean, bottom=bottom)
    bottom += weight_count

  ax.set_title("Your expenses during current week")
  ax.legend(loc="upper right")

  if args.output:
    plt.savefig(f"{args.output}.png")
  else:
    plt.show()


if __name__ == '__main__':
  main()