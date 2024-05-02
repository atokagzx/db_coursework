from alchemy_contrib._models import BaseDB
import alchemy_contrib._models as am
from sqlalchemy import create_engine, exc as sqlalchemy_exc
from sqlalchemy.orm import sessionmaker
import os
import logging
import typing
import functools
from _utils import Singleton


class DBFacade(metaclass=Singleton):
    def __init__(self):
        user, host, port, database, password = self._get_credentials()
        self._logger = logging.getLogger("pg_facade")
        psqldb_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self._engine = create_engine(psqldb_url, pool_pre_ping=True)
        self._Session = sessionmaker(bind=self._engine, expire_on_commit=False)
        # self._session = None
        self._logger.info("connected to database")
        self.create_tables(recreate=False)

    def _get_credentials(self):
        POSTGRES_USER = os.environ["POSTGRES_USER"]
        POSTGRES_HOST = os.environ["POSTGRES_HOST"]
        POSTGRES_PORT = os.environ["POSTGRES_PORT"]
        POSTGRES_DB = os.environ["POSTGRES_DB"]
        POSTGRES_PASSWORD_FILE = os.environ["POSTGRES_PASSWORD_FILE"]
        try:
            with open(POSTGRES_PASSWORD_FILE, "r") as f:
                POSTGRES_PASSWORD = f.read().strip()
        except Exception as e:
            self._logger.error(f"could not read password file {POSTGRES_PASSWORD_FILE}")
            raise
        return (
            POSTGRES_USER,
            POSTGRES_HOST,
            POSTGRES_PORT,
            POSTGRES_DB,
            POSTGRES_PASSWORD,
        )

    @property
    def engine(self) -> create_engine:
        return self._engine
    
    @property
    def SMaker(self) -> sessionmaker:
        '''
        Returns a sessionmaker object.
        '''
        return self._Session

    def db_session(self):
        db_session = self.SMaker()
        try:
            yield db_session
        finally:
            db_session.close()


    # @property
    # def session(self):
    #     if self._session is None:
    #         Session = sessionmaker(bind=self._engine, expire_on_commit=False)
    #         self._session = Session()
    #     return self._session

    def create_tables(self, recreate=False):
        self._logger.info("creating tables")
        if recreate:
            self._logger.warning(
                "dropping tables before creating, because recreate=True"
            )
            self.drop_tables()
        BaseDB.metadata.create_all(bind=self._engine)
        # add default roles
        if recreate:
            self.add_default_roles()


    def drop_tables(self):
        self._logger.info("dropping tables")
        BaseDB.metadata.drop_all(bind=self._engine)

    def get_user(self, username):
        with self.SMaker() as session:
            # return user and roles
            user = session.query(am.User).filter(am.User.username == username).first()
            if user is None:
                return None, None
            roles = session.query(am.Role).join(am.UserRole).filter(am.UserRole.user_id == user.user_id).all()
            roles = [role.role_name for role in roles]
            return user, roles
        

    def register_user(self, username, password, roles, email):
        self._logger.info(f"registering user '{username}' with roles {roles}")
        timestamp = am.datetime.utcnow()
        user = am.User(username=username, password_hash=password, created_at=timestamp, email=email)
        with self.SMaker() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            for role in roles:
                role = session.query(am.Role).filter(am.Role.role_name == role).first()
                if role is None:
                    self._logger.error(f"role '{role}' does not exist")
                    continue
                user_role = am.UserRole(user_id=user.user_id, role_id=role.role_id)
                session.add(user_role)
                session.commit()
        return user
    

    def add_default_roles(self):
        with self.SMaker() as session:
            roles = [
                am.Role(role_name="admin"),
                am.Role(role_name="instructor"),
                am.Role(role_name="student"),
            ]
            session.add_all(roles)
            session.commit()
        return roles
