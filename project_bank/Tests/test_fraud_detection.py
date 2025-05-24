import pytest
from Models.blacklist import detect_fraud
from Models import transaction
from Models.blacklist import is_fraudulent_transaction

def test_blacklist_sender():
    blacklist = {'SE3550000000054910000003'}
    txn = transaction(sender_iban='SE3550000000054910000003', receiver_iban='SE4550000000054910000004', amount=1000, currency_code='SEK')
    is_fraud, reason = detect_fraud(txn, blacklist)
    assert is_fraud is True
    assert reason == "Sender is blacklisted"

def test_blacklist_receiver():
    blacklist = {'SE4550000000054910000004'}
    txn = transaction(sender_iban='SE3550000000054910000003', receiver_iban='SE4550000000054910000004', amount=1000, currency_code='SEK')
    is_fraud, reason = detect_fraud(txn, blacklist)
    assert is_fraud is True
    assert reason == "Receiver is blacklisted"

def test_amount_threshold():
    blacklist = set()
    txn = transaction(sender_iban='SE3550000000054910000003', receiver_iban='SE4550000000054910000004', amount=200000, currency_code='SEK')
    is_fraud, reason = detect_fraud(txn, blacklist)
    assert is_fraud is True
    assert reason == "Amount exceeds threshold"

def test_no_fraud():
    blacklist = set()
    txn = transaction(sender_iban='SE3550000000054910000003', receiver_iban='SE4550000000054910000004', amount=500, currency_code='SEK')
    is_fraud, reason = detect_fraud(txn, blacklist)
    assert is_fraud is False
    assert reason is None


def test_large_amount_flagged():
    tx = {'amount': 1000000, 'currency': 'USD'}
    assert is_fraudulent_transaction(tx) is True

def test_negative_amount():
    tx = {'amount': -500, 'currency': 'SEK'}
    assert is_fraudulent_transaction(tx) is True

def test_valid_transaction():
    tx = {'amount': 100, 'currency': 'SEK'}
    assert is_fraudulent_transaction(tx) is False

def test_duplicate_transaction():
    tx1 = {'transaction_id': 'abc123'}
    tx2 = {'transaction_id': 'abc123'}
    seen = {tx1['transaction_id']}
    assert tx2['transaction_id'] in seen