# import csv
# from app.model import Quote

# def save_quotes_to_csv(quotes: Quote):
#     with open('quotes.csv', mode='a', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([quotes.vendor, quotes.item, quotes.price, quotes.date.isoformat()])

# def load_quotes_from_csv() -> list[Quote]:
#     quotes= []
#     try:
#         with open('quotes.csv', mode='r') as file:
#             reader = csv.reader(file)
#             for row in reader:
#                 if len(row) == 4:
#                     vendor, item, price, date = row
#                     quotes.append(Quote(vendor=vendor, item=item, price=float(price), date=date))
#     except FileNotFoundError:
#         pass # File does not exist, return empty list
#     return quotes
