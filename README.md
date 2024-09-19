Expense tracker cli app written in Python
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

You can omit all flags but you'll be prompted required fields which include amount, category and date. Description will be prompted as well but is optional

Edit expense with:
```
expenses update
```
This will ask you to pick an expense to update. It can be quieried by field or selected from latest. Lookup method can be selected with `--lookup` flag

To delete expense use:
```
expenses delete
```
This will ask you for expense the same way as update and ask for confirmation

To see your week's expenses run `python chart.py` which shows a nice stacked bar chart showing total spendings in each category spread across each of the weekdays

You can choose to save chart as an image by running `chart.py` with `--output` and specifying a filename