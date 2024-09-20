## Description
Expense tracker CLI app written in Python with the use of the Click package.
## Installation
```
poetry shell
poetry install
pip install --editable .
```

## Usage
Add expense with:
```
expenses create --amount AMOUNT --category CATEGORY --date DATE --description DESCRIPTION
```

All flags are otional. If you omit the flags you'll be prompted required fields which include amount, category and date. Description will be prompted as well but can be skipped.

You can see details of specific expense with:
```
expenses read 
```
This will ask you to pick an expense sorted by most recent by default. To aid in lookup you can use `--filter` and `--sort` flags with a name of a field, which will prompt you for a value. Use `--help` to see all available options.

Edit expense with:
```
expenses update
```
This will prompt you for an expense and a field to edit. Same lookup flags as read can be applied.

To delete expense use:
```
expenses delete
```
This will ask you for expense the same way as update or read commands and ask for confirmation. Lookup flags apply here as well.

To see your week's expenses run 
```
python chart.py
```
 which shows a nice stacked bar chart showing total spendings in each category spread across each of the weekdays

You can choose to save chart as an image by running it with `--output` and specifying a filename