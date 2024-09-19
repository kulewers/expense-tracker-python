from sqlalchemy.orm import Session
import click

from database import engine
import models

from datetime import datetime, date
from math import ceil


@click.command
@click.option("--amount", "-a", prompt=True, help="Amount spend", required=True)
@click.option("--category", "-c", prompt=True, help="Category of the expense", default="Other")
@click.option("--date", "-d", prompt=True, help="Date of the expense", default=date.today())
@click.option("--description", "-D", prompt=True, help="Description of the expense", default="", show_default="None")
def create(amount: float, category: str, date: date, description: str):
  with Session(engine) as session:
    with session.begin():
      db_expense = models.Expense(
        amount=amount,
        category=category, 
        date=datetime.strptime(date, "%Y-%m-%d").date(),
        description=description
      )
      session.add(db_expense)
      session.commit()
      print("Expense added")


@click.command
@click.option('--lookup', prompt=True, type=click.Choice(['latest', 'byvalue']), default='latest')
def update(lookup: str):
  with Session(engine) as session:
    with session.begin():
      query = session.query(models.Expense).order_by(models.Expense.date.desc())
      if lookup == 'byvalue':
        query = filter_query(query)
      try:
        expense = paginate_query(query)
      except Exception as e:
        print(e)
        exit()
      while True:
        value = click.prompt("Select field to update", type=click.Choice(['amount', 'category', 'date', 'description']))
        if value == 'amount':
          amount = click.prompt("Amount", type=float) 
          expense.amount = amount
        elif value == 'category':
          category = click.prompt("Category", type=str, default="Other") 
          expense.category = category
        elif value == 'date':
          date_str = click.prompt("Date", default=date.today())
          date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
          expense.date = date_object
        elif value == 'description':
          description = click.prompt("Description", type=str)
          expense.description = description
        if not click.confirm("Do you wish to update any more fields?"):
          session.commit()
          exit()


@click.command()
@click.option('--lookup', prompt=True, type=click.Choice(['latest', 'byvalue']), default='latest')
def delete(lookup: str):
  with Session(engine) as session:
    with session.begin():
      query = session.query(models.Expense).order_by(models.Expense.date.desc())
      if lookup == 'byvalue':
        query = filter_query(query)
      try:
        expense = paginate_query(query)
      except Exception as e:
        print(e)
        exit()
      if click.confirm(f"Are you sure you want to delete expense {expense}?"):
        session.delete(expense)
        session.commit()


def filter_query(query):
  value = click.prompt("Select field to filter", type=click.Choice(['amount', 'category', 'date', 'description']))
  if value == 'amount':
    amount = click.prompt("Amount", type=float)
    query = query.filter(models.Expense.amount == amount)
    return query
  elif value == 'category':
    category = click.prompt("Category", type=str, default="Other")
    query = query.filter(models.Expense.category.contains(category))
    return query
  elif value == 'date':
    date_str = click.prompt("Date", default=date.today())
    date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
    query = query.filter(models.Expense.date == date_object)
    return query
  elif value == 'description':
    description = click.prompt("Description", type=str)
    query = query.filter(models.Expense.description.contains(description))
    return query


def paginate_query(query, offset: int = 0, page: int = 1, page_size: int = 5) -> models.Expense:
  expenses = query.offset(offset).limit(page_size).all()
  total = query.count()
  if total == 0:
    raise Exception("Query returned empty result")
  page_count = ceil(total/page_size)
  print(f"Showing page {page} of {page_count}")

  options = []
  for idx, expense in enumerate(expenses, start=1):
    options.append(expense)
    print(f"{idx}) {expense}")

  if page > 1:
    options.append('back')
    print(f"{len(options)}) Back")

  if not page_count == page:
    options.append('load more')
    print(f"{len(options)}) Load more") 

  choice = 0
  while not (choice > 0 and choice <= len(options)):
    try:
      choice = int(input())
    except ValueError:
      print("Expected integer value")

  answer = options[choice-1]

  if answer is models.Expense:
    return answer
  
  if answer == 'load more':
    return paginate_query(query, offset=offset+page_size, page=page+1, page_size=page_size)

  if answer == 'back':
    return paginate_query(query, offset=offset-page_size, page=page-1, page_size=page_size)
