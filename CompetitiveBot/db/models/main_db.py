from sqlalchemy import create_engine, Column, VARCHAR, TEXT, DATE, String, ForeignKey
from dotenv import load_dotenv
from sqlalchemy.orm import scoped_session, declarative_base, sessionmaker
import datetime
#from config import settings

load_dotenv()

#host = settings.host
#password = settings.password
#database = settings.database

#engine = create_engine(f"postgresql+psycopg2://postgres:{password}@{host}/{database}")

#session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
#Base.query = session.query_property()