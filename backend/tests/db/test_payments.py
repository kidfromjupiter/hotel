from decimal import Decimal
from uuid import UUID

from app.repositories.billing_repo import BillingRepo


INVOICE_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_partial_payments_and_checkout_do_not_create_extra_transaction(db_connection):
    with db_connection.cursor() as cursor:
        cursor.execute("DELETE FROM transactions WHERE invoice_id = %s", (str(INVOICE_ID),))
        cursor.execute(
            "UPDATE billing_summary SET amount_paid = 0, payment_status = 'UNPAID' "
            "WHERE invoice_id = %s",
            (str(INVOICE_ID),),
        )

    repo = BillingRepo(db_connection)
    blocked = repo.checkout_booking(1001)
    assert blocked["error_code"] == "OUTSTANDING_BALANCE"

    first = repo.record_payment(INVOICE_ID, Decimal("20000.00"), "Cash")
    assert first["success"] is True
    assert first["payment_status"] == "PARTIALLY_PAID"
    assert Decimal(str(first["outstanding_balance"])) == Decimal("54290.00")

    overpayment = repo.record_payment(INVOICE_ID, Decimal("54290.01"), "Card")
    assert overpayment["error_code"] == "OVERPAYMENT"

    second = repo.record_payment(INVOICE_ID, Decimal("54290.00"), "Card")
    assert second["success"] is True
    assert second["payment_status"] == "PAID"
    assert second["transaction_id"] != first["transaction_id"]
    assert Decimal(str(second["outstanding_balance"])) == 0

    checked_out = repo.checkout_booking(1001)
    assert checked_out["success"] is True
    assert repo.checkout_booking(1001)["error_code"] == "INVALID_STATUS"
    assert repo.record_payment(INVOICE_ID, Decimal("1.00"), "Cash")["error_code"] == "INVALID_STATUS"

    with db_connection.cursor() as cursor:
        cursor.execute(
            "SELECT amount_paid, payment_status FROM billing_summary WHERE invoice_id = %s",
            (str(INVOICE_ID),),
        )
        amount_paid, status = cursor.fetchone()
        assert amount_paid == Decimal("74290.00")
        assert status == "PAID"

        cursor.execute(
            "SELECT amount, payment_method FROM transactions WHERE invoice_id = %s "
            "ORDER BY payment_date, amount",
            (str(INVOICE_ID),),
        )
        assert sorted(cursor.fetchall()) == [
            (Decimal("20000.00"), "Cash"),
            (Decimal("54290.00"), "Card"),
        ]


def test_payment_requires_checked_in_booking(db_connection):
    repo = BillingRepo(db_connection)
    result = repo.record_payment(
        UUID("77777777-7777-7777-7777-777777777777"), Decimal("1.00"), "Cash"
    )
    assert result["error_code"] == "INVALID_STATUS"
