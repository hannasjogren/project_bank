"""
Komplett migration: customers, accounts, transactions, validation logs,
currency rates, orphaned transactions and triggers.
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Skapa customers tabell
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('ssn', sa.String(12), unique=True, nullable=False),
        sa.Column('email', sa.String(255)),
        sa.Column('phone_number', sa.String(15)),
        sa.Column('country', sa.String(100)),
        sa.Column('municipality', sa.String(100))
    )

    # Skapa accounts tabell
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('iban', sa.String(34), unique=True, nullable=False),
        sa.Column('customer_id', sa.Integer, sa.ForeignKey('customers.id', ondelete="CASCADE"), nullable=False),
        sa.Column('balance', sa.Numeric(12, 2), default=0)
    )

    # Skapa currency_rates tabell
    op.create_table(
        'currency_rates',
        sa.Column('currency_code', sa.String(10), primary_key=True),
        sa.Column('rate_to_sek', sa.Numeric(12, 6), nullable=False)
    )

    # Skapa transactions tabell
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('sender_account', sa.String(34), sa.ForeignKey('accounts.iban', ondelete="CASCADE"), nullable=False),
        sa.Column('receiver_account', sa.String(34), sa.ForeignKey('accounts.iban', ondelete="CASCADE"), nullable=False),
        sa.Column('sender_country', sa.String(100), nullable=False),
        sa.Column('receiver_country', sa.String(100), nullable=False),
        sa.Column('description', sa.String, default="Unknown"),
        sa.CheckConstraint("currency IN ('USD', 'EUR', 'SEK', 'GBP')", name='chk_currency'),
        sa.CheckConstraint("amount >= 0", name='chk_amount')
    )

    # Skapa validation_logs tabell
    op.create_table(
        'validation_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('transaction_id', sa.Integer, sa.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False),
        sa.Column('is_valid', sa.Boolean, nullable=False),
        sa.Column('validation_reason', sa.String, nullable=False)
    )

    # Skapa orphaned_transactions tabell
    op.create_table(
        'orphaned_transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.String(34), sa.ForeignKey("accounts.iban", ondelete="SET NULL")),
        sa.Column('original_amount', sa.Numeric(12, 2)),
        sa.Column('currency', sa.String(10)),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

    # Skapa customer_log tabell
    op.create_table(
        'customer_log',
        sa.Column('log_id', sa.Integer, primary_key=True),
        sa.Column('customer_id', sa.Integer, sa.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now())
    )

    # Skapa transaction_log tabell
    op.create_table(
        'transaction_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('transaction_id', sa.Integer, sa.ForeignKey('transactions.id', ondelete="CASCADE")),
        sa.Column('action', sa.String(50)),
        sa.Column('timestamp', sa.TIMESTAMP, server_default=sa.func.now())
    )

    # Lägg triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION log_transaction() RETURNS trigger AS $$
        BEGIN
            INSERT INTO transaction_log(transaction_id, action)
            VALUES (NEW.id, 'INSERT');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_log_transaction
        AFTER INSERT ON transactions
        FOR EACH ROW
        EXECUTE FUNCTION log_transaction();
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION log_new_customer() RETURNS trigger AS $$
        BEGIN
            INSERT INTO customer_log(customer_id, timestamp) VALUES (NEW.id, now());
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_log_new_customer
        AFTER INSERT ON customers
        FOR EACH ROW
        EXECUTE FUNCTION log_new_customer();
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION flag_missing_account() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM accounts WHERE iban = NEW.sender_account) THEN
                INSERT INTO orphaned_transactions(account_id, original_amount, currency, timestamp)
                VALUES (NEW.sender_account, NEW.amount, NEW.currency, now());
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_flag_missing_account
        BEFORE INSERT ON transactions
        FOR EACH ROW
        EXECUTE FUNCTION flag_missing_account();
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION convert_currency() RETURNS trigger AS $$
        DECLARE
            rate NUMERIC(12,6);
        BEGIN
            SELECT rate_to_sek INTO rate FROM currency_rates WHERE currency_code = NEW.currency;
            IF rate IS NULL THEN
                RAISE EXCEPTION 'No conversion rate for currency: %', NEW.currency;
            END IF;
            NEW.amount := NEW.amount * rate;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_convert_currency
        BEFORE INSERT ON transactions
        FOR EACH ROW
        EXECUTE FUNCTION convert_currency();
    """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trigger_convert_currency ON transactions")
    op.execute("DROP FUNCTION IF EXISTS convert_currency")
    op.execute("DROP TRIGGER IF EXISTS trigger_flag_missing_account ON transactions")
    op.execute("DROP FUNCTION IF EXISTS flag_missing_account")
    op.execute("DROP TRIGGER IF EXISTS trigger_log_new_customer ON customers")
    op.execute("DROP FUNCTION IF EXISTS log_new_customer")
    op.execute("DROP TRIGGER IF EXISTS trigger_log_transaction ON transactions")
    op.execute("DROP FUNCTION IF EXISTS log_transaction")
    op.drop_table('transaction_log')
    op.drop_table('customer_log')
    op.drop_table('orphaned_transactions')
    op.drop_table('validation_logs')
    op.drop_table('transactions')
    op.drop_table('accounts')
    op.drop_table('currency_rates')
    op.drop_table('customers')