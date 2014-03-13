from sqlalchemy import Column, Integer, String

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    twitter = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', twitter='%s')>" % (
                            self.name, self.fullname, self.twitter)

from sqlalchemy.orm import sessionmaker

def create_engine_from_params(dbname, user, password, host, port, echo=True):

    Session = sessionmaker()

    connection_url_template = (r'postgresql+psycopg2://'
                               r'{user}:{password}@{host}:{port}/{dbname}')

    connection_url = connection_url_template.format(user=user,
                                                    password=password,
                                                    host=host,
                                                    port=port,
                                                    dbname=dbname)

    engine = create_engine(connection_url, echo=echo)

    # Will create the tables synchronously
    Base.metadata.create_all(engine)
    return engine
