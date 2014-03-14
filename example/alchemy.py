from sqlalchemy import Column, Integer, String

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

import sqlalchemy.dialects.postgres

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

def create_engine_from_params(dbname="postgres", user="postgres", password="",
                              host="localhost", port="5432", echo=True):

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


def bridge_query(query, engine):
    '''
    Conducts a query on the raw engine given, binding the objects to the model
    given.

    Queries don't necessarily have to use Sessions to set up the right constructs

    >>> import sqlalchemy
    >>> import sqlalchemy.orm.query
    >>> sqlalchemy.orm.query.Query(User, User.name)

    >>> # This will fail
    >>> sqlalchemy.orm.query.Query(User).one()

    >>> # Need to limit instead
    >>> sqlalchemy.orm.query.Query(User, User.name).limit(1)


    '''
    result_proxy = get_result(query, engine)

    # TODO: Coerce results into the right model

    return result_proxy

def get_result(query, engine):
  # Work with Postgres
  dialect = sqlalchemy.dialects.postgres.dialect()

  query.enable_eagerloads(False)
  raw_sql = unicode(query.statement.compile(dialect=dialect))
  print(raw_sql)
  print("*"*32)

  # Returns a ResultProxy, each row is a RowProxy
  results = engine.execute(raw_sql)

  # Not what the rest of the code will expect
  # We're expecting the actual Model object
  # Each RowProxy is a dict
  return results



if __name__ == "__main__":
    engine = create_engine_from_params()
    import sqlalchemy.orm.query

    # query without a session
    query = sqlalchemy.orm.query.Query(User, User.name)

    #Session = sessionmaker(bind=engine)
    #session = Session()

    #query = session.query(User)

    result = bridge_query(query, engine)
