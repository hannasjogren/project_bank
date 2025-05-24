from alembic import op
import sqlalchemy as sa

def upgrade():
    # Skapa currency_rates
    op.create_table(
        'currency_rates',
        sa.Column('currency_code', sa.String, primary_key=True),
        sa.Column('rate_to_sek', sa.Float, nullable=False)
    )

    # Skapa customer_log
    op.create_table(
        'customer_log',
        sa.Column('log_id', sa.Integer, primary_key=True),
        sa.Column('customer_id', sa.Integer),
        sa.Column('timestamp', sa.DateTime)
    )

    # Skapa orphaned_transactions
    # Skapar en ny databastabell som heter orphaned_transactions. 
    # Det är en tabell som används för att spara transaktioner som inte hör till någon känd kund eller konto.
    op.create_table(
        'orphaned_transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer),
        sa.Column('original_amount', sa.Float),
        sa.Column('timestamp', sa.DateTime)
    )

    # Lägg triggers
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
        IF NOT EXISTS (SELECT 1 FROM accounts WHERE id = NEW.account_id) THEN
            INSERT INTO orphaned_transactions(account_id, original_amount, timestamp)
            VALUES (NEW.account_id, NEW.amount, now());
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
        rate FLOAT;
    BEGIN
        SELECT rate_to_sek INTO rate FROM currency_rates WHERE currency_code = NEW.currency_code;
        IF rate IS NULL THEN
            RAISE EXCEPTION 'No conversion rate for currency: %', NEW.currency_code;
        END IF;
        NEW.amount_in_sek := NEW.amount * rate;
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
    op.drop_table('orphaned_transactions')
    op.drop_table('customer_log')
    op.drop_table('currency_rates')