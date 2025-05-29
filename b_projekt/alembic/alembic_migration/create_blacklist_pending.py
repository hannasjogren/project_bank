"""Create blacklist and pending_transactions tables"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# Revision metadata
revision = "20240529_blacklist_pending"
down_revision = None  # Ange tidigare revision om detta är en uppdatering
branch_labels = None
depends_on = None

def upgrade():
    # Skapa blacklist-tabellen
    op.create_table(
        "blacklist",
        sa.Column("account_iban", sa.String(34), sa.ForeignKey("accounts.iban"), primary_key=True),
        sa.Column("reason", sa.String, nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("sender_country", sa.String(50), nullable=False),
        sa.Column("receiver_country", sa.String(50), nullable=False),
        sa.Column("flagged_at", sa.DateTime, default=datetime.now),
        sa.CheckConstraint("amount > 100000", name="valid_amount"),
        sa.CheckConstraint("length(account_iban) >= 15 AND length(account_iban) <= 34", name="valid_iban"),
        sa.CheckConstraint("sender_country <> receiver_country", name="different_countries"),
    )

    # Skapa pending_transactions-tabellen
    op.create_table(
        "pending_transactions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("sender_account", sa.String(34), nullable=False),
        sa.Column("receiver_account", sa.String(34), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String, default="pending"),
        sa.Column("created_at", sa.DateTime, default=datetime.now),
        sa.CheckConstraint("amount > 0", name="valid_amount"),
        sa.CheckConstraint("sender_account <> receiver_account", name="different_accounts"),
        sa.CheckConstraint("length(currency) = 3", name="valid_currency_code"),
        sa.CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="valid_status"),
    )

def downgrade():
    # Ta bort tabeller vid rollback
    op.drop_table("blacklist")
    op.drop_table("pending_transactions")