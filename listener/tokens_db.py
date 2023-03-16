from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Tokens(Base):
    __tablename__ = 'tokens_db'

    id = Column(Integer, primary_key=True)
    serial = Column(String)
    status = Column(String)


engine = create_engine('postgresql://postgres:postgres@localhost/tokens')
Base.metadata.create_all(engine)


def save_to_database(serial, status):
    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create a new Token object and add it to the session
    new_token = Tokens(serial=serial, status=status)
    session.add(new_token)

    # Commit the transaction and close the session
    session.commit()
    session.close()
