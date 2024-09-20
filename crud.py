from sqlalchemy.orm import Session
import click

from database import engine
import models

from datetime import datetime, date
from math import ceil


@click.command
@click.option('--amount', '-a', prompt=True, help='Amount spend', required=True)
@click.option('--category', '-c', prompt=True, help='Category of the expense', default='Other')
@click.option('--date', '-d', prompt=True, help='Date of the expense', default=date.today())
@click.option('--description', '-D', prompt=True, help='Description of the expense', default='', show_default='None')
def create(amount: float, category: str, date: date, description: str):
  with Session(engine) as session:
    with session.begin():
      db_expense = models.Expense(
        amount=amount,
        category=category, 
        date=datetime.strptime(date, '%Y-%m-%d').date(),
        description=description
      )
      session.add(db_expense)
      session.commit()
      print('Expense added')


@click.command
@click.option('--filter', '-f', type=click.Choice(['amount', 'category', 'date', 'description', 'amount__range', 'date__range']), default=[], multiple=True)
@click.option('--sort', '-s', type=click.Choice(['date', 'amount', 'category', 'description', 'date__asc', 'amount__asc']), default=['date'], multiple=True)
def read(filter: str, sort: str):
  with Session(engine) as session:
    with session.begin():
      query = session.query(models.Expense)
      query = sort_query(query, sort)
      if filter:
        query = filter_query(query, filter)
      expense = paginate_query(query)
      print(f'Amount: {expense.amount}')
      print(f'Category: {expense.category}')
      print(f'Date: {expense.date}')
      if expense.description:
        print(f'Description: {expense.description}')
      else:
        print('Description not provided')


@click.command
@click.option('--filter', '-f', type=click.Choice(['amount', 'category', 'date', 'description', 'amount__range', 'date__range']), default=[], multiple=True)
@click.option('--sort', '-s', type=click.Choice(['date', 'amount', 'category', 'description', 'date__asc', 'amount__asc']), default=['date'], multiple=True)
def update(filter: str, sort: str):
  with Session(engine) as session:
    with session.begin():
      query = session.query(models.Expense)
      if filter:
        query = filter_query(query, filter)
      try:
        expense = paginate_query(query)
      except Exception as e:
        print(e)
        exit()
      while True:
        value = click.prompt('Select field to update', type=click.Choice(['amount', 'category', 'date', 'description']))
        if value == 'amount':
          amount = click.prompt('Amount', type=float) 
          expense.amount = amount
        elif value == 'category':
          category = click.prompt('Category', type=str, default='Other') 
          expense.category = category
        elif value == 'date':
          date_str = click.prompt('Date', default=date.today())
          date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
          expense.date = date_object
        elif value == 'description':
          description = click.prompt('Description', type=str)
          expense.description = description
        if not click.confirm('Do you wish to update any more fields?'):
          session.commit()
          exit()


@click.command()
@click.option('--filter', '-f', type=click.Choice(['amount', 'category', 'date', 'description', 'amount__range', 'date__range']), default=[], multiple=True)
@click.option('--sort', '-s', type=click.Choice(['date', 'amount', 'category', 'description', 'date__asc', 'amount__asc']), default=['date'], multiple=True)
def delete(filter: str, sort: str):
  with Session(engine) as session:
    with session.begin():
      query = session.query(models.Expense)
      query = sort_query(query, sort)
      if filter:
        query = filter_query(query, filter)
      try:
        expense = paginate_query(query)
      except Exception as e:
        print(e)
        exit()
      if click.confirm(f'Are you sure you want to delete expense {expense}?'):
        session.delete(expense)
        session.commit()

    
def sort_query(query, sort):
  for value in sort:
    match value:
      case 'date':
        query = query.order_by(models.Expense.date.desc()) 
      case 'amount':
        query = query.order_by(models.Expense.amount.desc())
      case 'date__asc':
        query = query.order_by(models.Expense.date.asc()) 
      case 'amount__asc':
        query = query.order_by(models.Expense.amount.asc())
      case 'category':
        query = query.order_by(models.Expense.category.asc())
      case 'description':
        query = query.order_by(models.Expense.description.asc())

  return query


def filter_query(query, filter):
  for value in filter:
    match value:
      case 'amount':
        amount = click.prompt('Amount', type=float)
        query = query.filter(models.Expense.amount == amount)
      case 'category':
        category = click.prompt('Category', type=str, default='Other')
        query = query.filter(models.Expense.category.contains(category))
      case 'date':
        date_str = click.prompt('Date', default=date.today())
        date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
        query = query.filter(models.Expense.date == date_object)
      case 'description':
        description = click.prompt('Description', type=str)
        query = query.filter(models.Expense.description.contains(description))
      case 'amount__range':
        lower_bound = click.prompt('Amount (Lower bound)', type=float)
        upper_bound = click.prompt('Amount (Upper bound)', type=float)
        query = query.filter(models.Expense.amount.between(lower_bound, upper_bound))
      case 'date__range':
        lower_bound = click.prompt('Date (Lower bound)', default=date.today())
        upper_bound = click.prompt('Date (Upper bound)', default=date.today())
        query = query.filter(models.Expense.date.between(lower_bound, upper_bound))
      case _:
        raise Exception('Unknkown type')
  return query

def paginate_query(query, offset: int = 0, page: int = 1, page_size: int = 5) -> models.Expense:
  expenses = query.offset(offset).limit(page_size).all()
  total = query.count()
  if total == 0:
    raise Exception('Query returned empty result')
  page_count = ceil(total/page_size)
  print(f'Showing page {page} of {page_count}')

  options = []
  for idx, expense in enumerate(expenses, start=1):
    options.append(expense)
    opt = f'{idx}) {expense.amount} on {expense.category}, {expense.date}'
    if expense.description:
      opt += f' ("{expense.description}")'
    print(opt)


  if page > 1:
    options.append('back')
    print(f'{len(options)}) Back')

  if not page_count == page:
    options.append('load more')
    print(f'{len(options)}) Load more') 

  choice = click.prompt(text='Option', type=click.IntRange(0, len(options)))

  answer = options[choice-1]

  if type(answer) is models.Expense:
    return answer
  
  if answer == 'load more':
    return paginate_query(query, offset=offset+page_size, page=page+1, page_size=page_size)

  if answer == 'back':
    return paginate_query(query, offset=offset-page_size, page=page-1, page_size=page_size)
