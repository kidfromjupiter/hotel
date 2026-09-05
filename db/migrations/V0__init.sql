create table transactions (
  transaction_id UUID PRIMARY KEY,
  invoice_id UUID,
  payment_date TIMESTAMP,
  amount NUMERIC(10,2)
)
