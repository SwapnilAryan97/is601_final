import logging

from app import db
from app.db.models import User, Transaction
from faker import Faker
from sqlalchemy.sql import functions


def test_add_user(application):
    log = logging.getLogger("myApp")
    with application.app_context():
        assert db.session.query(User).count() == 0
        assert db.session.query(Transaction).count() == 0
        user = User('test@test', 'testtest')
        db.session.add(user)
        db.session.commit()
        assert db.session.query(User).count() == 1


def test_access_user(application, add_user):
    with application.app_context():
        user = User.query.filter_by(email='test@test').first()
        assert db.session.query(User).count() == 2
        # log.info(user)
        assert user.email == 'test@test'
        assert user.active == True


def test_first_balance(application, add_user):
    with application.app_context():
        user = User.query.filter_by(email='test@test').first()
        assert user.inital_balance == 0
        assert user.get_balance() == 0


def test_add_transactions(application, add_user):
    with application.app_context():
        user = User.query.filter_by(email='test@test').first()
        user.transactions = [Transaction(3000, 'CREDIT'), Transaction(-2000, 'DEBIT')]
        db.session.commit()
        # checking no of transactions for user tnvrra393@gmail.com
        assert len(user.transactions) == 2
        assert db.session.query(Transaction).count() == 2


def test_balance_after_transaction(application, add_user):
    with application.app_context():
        user = User.query.filter_by(email='test@test').first()
        user.transactions = [Transaction(3000, 'CREDIT'), Transaction(-2000, 'DEBIT')]
        db.session.commit()
        # checking no of transactions for user tnvrra393@gmail.com
        assert len(user.transactions) == 2
        assert db.session.query(Transaction).count() == 2
        result = db.session.query(functions.sum(Transaction.amount)).scalar()
        assert result == 1000


def test_adding_different_user_transaction(application, add_user):
    with application.app_context():
        user = User.query.filter_by(email='test@test').first()
        user1 = User.query.filter_by(email='test2@test').first()
        user.transactions = [Transaction(3000, 'CREDIT'), Transaction(-2000, 'DEBIT')]
        user1.transactions = [Transaction(5000, 'CREDIT'), Transaction(-1500, 'DEBIT'), Transaction(-500, 'DEBIT')]
        db.session.commit()
        # checking no of transactions for user tnvrra393@gmail.com
        assert len(user.transactions) == 2
        # checking no of transactions for user vishnu@gmail.com
        assert len(user1.transactions) == 3
        # Check total transactions in tabel
        assert db.session.query(Transaction).count() == 5


def test_changing_user_transactions_check_balance(application, add_user):
    with application.app_context():
        user = User.query.filter_by(email='test@test').first()
        user.transactions = [Transaction(3000, 'CREDIT'), Transaction(-2000, 'DEBIT')]
        db.session.commit()
        result = db.session.query(functions.sum(Transaction.amount)).scalar()
        assert result == 1000
        transaction1 = Transaction.query.filter_by(amount=3000).first()
        transaction1.amount = 4000
        db.session.commit()
        result = db.session.query(functions.sum(Transaction.amount)).scalar()
        assert result == 2000
        user.transactions.append(Transaction(2000, 'CREDIT'))
        db.session.commit()
        assert len(user.transactions) == 3
        result = db.session.query(functions.sum(Transaction.amount)).scalar()
        assert result == 4000


def test_delete_user(application, add_user):
    with application.app_context():
        user = User.query.filter_by(email='test@test').first()
        user.transactions = [Transaction(3000, 'CREDIT'), Transaction(-2000, 'DEBIT')]
        assert db.session.query(Transaction).count() == 2
        db.session.delete(user)
        assert db.session.query(Transaction).count() == 0
