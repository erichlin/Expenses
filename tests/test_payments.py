from unittest import TestCase

import payments
import pandas as pd

class TestPayments(TestCase):
    def test_payments_transfers_balance(self):
        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 6, 4]],
            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person2', 'Person1', 4)],
            payments.compute_entries(df)
        )
    def test_payments_handles_taxes(self):
        df = pd.DataFrame(
            [['Expense 1', 15, 10, 'Person1', 6, 4]],
            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person2', 'Person1', 6)],
            payments.compute_entries(df)
        )
    def test_payments_handles_multiple_people(self):
        df = pd.DataFrame(
            [['Expense 1', 15, 10, 'Person1', 6, 3, 1]],
            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2', 'Person3'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person2', 'Person1', 4.5),
            payments.PaymentEntry('Person3', 'Person1', 1.5)],
            payments.compute_entries(df)
        )
    def test_payments_handles_pay_for_others(self):
        df = pd.DataFrame(
            [['Expense 1', 15, 10, 'Person1', 0, 10]],
            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person2', 'Person1', 15)],
            payments.compute_entries(df)
        )
    def test_payments_handles_multiple_entries(self):
        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 6, 4],
            ['Expense 2', 10, 10, 'Person1', 3, 7]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person2', 'Person1', 11)],
            payments.compute_entries(df)
        )
    def test_payments_debtor_pays_multiple_creditors(self):
        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 0,0,10],
            ['Expense 2', 10, 10, 'Person2', 0,0,10]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2', 'Person3'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person3', 'Person1', 10),
             payments.PaymentEntry('Person3', 'Person2', 10)],
            payments.compute_entries(df)
        )
    def test_payments_debtors_pay_same_creditor(self):
        df = pd.DataFrame(
            [['Expense 1', 20, 20, 'Person1', 0,10,10]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2', 'Person3'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person2', 'Person1', 10),
             payments.PaymentEntry('Person3', 'Person1', 10)],
            payments.compute_entries(df)
        )

    def test_payments_debtors_pay_same_creditor_and_different_creditor(self):
        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 0, 0, 0, 10, 0],
             ['Expense 2', 20, 20, 'Person2', 0, 0, 0, 10, 10],
             ['Expense 3', 10, 10, 'Person3', 0, 0, 0, 0, 10]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2', 'Person3', 'Person4', 'Person5'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person4', 'Person1', 10),
             payments.PaymentEntry('Person4', 'Person2', 10),
             payments.PaymentEntry('Person5', 'Person2', 10),
             payments.PaymentEntry('Person5', 'Person3', 10)],
            payments.compute_entries(df)
        )

    def test_payments_asserts_if_total_expenses_does_not_match_plus_or_minus(self):
        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 0, 9.98]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])
        payments.compute_entries(df)

        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 0, 10.02]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])
        payments.compute_entries(df)

        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 0, 9.97]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])

        with self.assertRaises(payments.ExpenseChecksumInputError):
            payments.compute_entries(df)

        df = pd.DataFrame(
            [['Expense 1', 10, 10, 'Person1', 0, 10.03]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2'])

        with self.assertRaises(payments.ExpenseChecksumInputError):
            payments.compute_entries(df)

    def test_payments_mix_debt_and_credit(self):
        df = pd.DataFrame(
            [['Expense 1', 20, 20, 'Person1', 0,10,10],
            ['Expense 2', 10, 10, 'Person2', 5,0,5],
             ['Expense 3', 6, 6, 'Person3', 3, 3, 0],
             ],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2', 'Person3'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person2', 'Person1', 3),
             payments.PaymentEntry('Person3', 'Person1', 9)],
            payments.compute_entries(df)
        )

    def test_payments_fewest_payments_favor_first_named_debtor_to_first_named_creditor(self):
        df = pd.DataFrame(
            [['Expense 1', 20, 20, 'Person3', 10, 10, 0,0],
             ['Expense 2', 10, 10, 'Person4', 10, 0, 0,0]],

            columns=['Expense Name', 'Total', 'Subtotal', 'Payer', 'Person1', 'Person2', 'Person3', 'Person4'])
        payments.compute_entries(df)
        self.assertEqual(
            [payments.PaymentEntry('Person1', 'Person3', 20),
             payments.PaymentEntry('Person2', 'Person4', 10)],
            payments.compute_entries(df)
        )

