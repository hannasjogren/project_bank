#CHECK Constraints i PostgreSQL
from sqlalchemy import Table, Column, Integer, String, Boolean, JSON, MetaData, TIMESTAMP
from sqlalchemy.sql import func

metadata = MetaData()

validation_logs = Table(
    "validation_logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("expectation_type", String),
    Column("column_name", String),
    Column("success", Boolean),
    Column("result", JSON),
    Column("timestamp", TIMESTAMP, default=func.now())
)