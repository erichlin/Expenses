import pygsheets
import payments

gc = pygsheets.authorize(service_file='client_secret.json')

sh = gc.open('Ski Trip Expenses')
wks = sh.sheet1
df = wks.get_as_df()
df.replace('', float("NaN"), inplace=True)
df.dropna(axis='columns', how='all', inplace=True)

payment_entries = payments.compute_entries(df)
for payment_entry in payment_entries:
    print(payment_entry.debtor, "pays", payment_entry.creditor, "$", payment_entry.amount)

