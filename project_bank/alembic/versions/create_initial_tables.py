"""
Initial migration: create customers, accounts, transactions and triggers.
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
        sa.Column('customer_id', sa.Integer, sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('balance', sa.Numeric, default=0)
    )

    # Skapa transactions tabell
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('sender_iban', sa.String(34), sa.ForeignKey('accounts.iban'), nullable=False),
        sa.Column('receiver_iban', sa.String(34), sa.ForeignKey('accounts.iban'), nullable=False),
        sa.Column('sender_country', sa.String(100)),
        sa.Column('sender_municipality', sa.String(100)),
        sa.Column('receiver_country', sa.String(100)),
        sa.Column('receiver_municipality', sa.String(100)),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('notes', sa.Text),
        sa.Column('timestamp', sa.TIMESTAMP, server_default=sa.func.now()),
        sa.CheckConstraint("transaction_type IN ('incoming', 'outgoing')", name='chk_transaction_type')
    )

    # Skapa logging tabell
    op.create_table(
        'transaction_log',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('transaction_id', sa.Integer),
        sa.Column('action', sa.String(50)),
        sa.Column('timestamp', sa.TIMESTAMP, server_default=sa.func.now())
    )

    # Skapa trigger function (PostgreSQL specific)
    op.execute("""
        CREATE OR REPLACE FUNCTION log_transaction()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO transaction_log(transaction_id, action)
            VALUES (NEW.id, 'INSERT');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Bind trigger till transactions
    op.execute("""
        CREATE TRIGGER trigger_log_transaction
        AFTER INSERT ON transactions
        FOR EACH ROW EXECUTE FUNCTION log_transaction();
    """)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trigger_log_transaction ON transactions")
    op.execute("DROP FUNCTION IF EXISTS log_transaction")
    op.drop_table('transaction_log')
    op.drop_table('transactions')
    op.drop_table('accounts')
    op.drop_table('customers')