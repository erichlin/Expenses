from collections import namedtuple

PaymentEntry = namedtuple('PaymentEntry',
                          'debtor, creditor, amount')

class ExpenseChecksumInputError(Exception):
    pass


def compute_entries(df):
    resolved_df = df.copy(deep=True)
    resolved_df['Implicit Tax'] = resolved_df['Total'] / resolved_df['Subtotal']

    maximum_error = 0.01 * (resolved_df.columns.size - 5)
    checksum = (resolved_df.iloc[:, 4:resolved_df.columns.size-1].sum(axis=1)*resolved_df['Implicit Tax']-resolved_df['Total']).abs()
    if (checksum > maximum_error).any():
        raise ExpenseChecksumInputError

    for column in resolved_df.columns[4:]:
        resolved_df.loc[column == resolved_df['Payer'], column] = resolved_df['Total'] - resolved_df[column] * resolved_df['Implicit Tax']
        resolved_df.loc[column != resolved_df['Payer'], column] = -1 * (resolved_df[column] * resolved_df['Implicit Tax'])
    owed_amounts = resolved_df.iloc[:, 4:resolved_df.columns.size - 1].sum()

    payment_entries = []

    for debtor, debt in owed_amounts.items():
        if debt < 0:
            for creditor, credit in owed_amounts.items():
                if credit > 0:
                    transfer = min(abs(owed_amounts[debtor]), abs(credit))
                    owed_amounts[debtor] += transfer
                    owed_amounts[creditor] -= transfer
                    payment_entries.append(PaymentEntry(debtor, creditor, transfer))
                    if owed_amounts[debtor] == 0:
                        break

    return payment_entries