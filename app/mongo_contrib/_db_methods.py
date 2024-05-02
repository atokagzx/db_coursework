import pymongo
from _utils import Singleton
import logging
import os
import json
from bson import ObjectId, json_util


class MongoFacade(metaclass=Singleton):
    def __init__(self):
        user, host, port, database, password = self._get_credentials()
        self._logger = logging.getLogger("mongo_facade")
        self._client = pymongo.MongoClient(host, int(port), username=user, password=password)
        self._db = self._client[database]
        self._logger.info("MongoFacade initialized")


    def _get_credentials(self):
        MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        MONGO_PASSWORD_FILE = os.getenv("MONGO_INITDB_ROOT_PASSWORD_FILE")
        MONGO_HOST = os.getenv("MONGO_HOST")
        MONGO_PORT = os.getenv("MONGO_PORT")
        MONGO_DB = os.getenv("MONGO_DB")
        try:
            with open(MONGO_PASSWORD_FILE, "r") as f:
                MONGO_PASSWORD = f.read().strip()
        except Exception as e:
            self._logger.error(f"could not read password file {MONGO_PASSWORD_FILE}")
            raise
        return MONGO_USER, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_PASSWORD
    

    @property
    def db(self):
        return self._db
    
    
    def create_material(self, content: str) -> str:
        '''
        Create a material.
        @param material_id: int
        @param content: str
        @return: url to the material
        '''
        collection = self._db["materials"]
        result = collection.insert_one({"content": content})
        self._logger.info(f"material created with id: {result.inserted_id}")
        return str(result.inserted_id)
    

    def get_materials(self, url: str) -> str:
        '''
        Get materials.
        @param url: str
        @return: dict
        '''
        collection = self._db["materials"]
        url = ObjectId(url)
        material = collection.find_one({"_id": url})
        return json_util.dumps(material["content"])
        

    def update_material(self, url: str, content: str) -> None:
        '''
        Update a material.
        @param url: str
        @param content: str
        '''
        collection = self._db["materials"]
        url = ObjectId(url)
        collection.update_one({"_id": url}, {"$set": {"content": content}})
        self._logger.info(f"material updated with id: {url}")


    def delete_material(self, url: str) -> None:
        '''
        Delete a material.
        @param url: str
        '''
        collection = self._db["materials"]
        url = ObjectId(url)
        collection.delete_one({"_id": url})
        self._logger.info(f"material deleted with id: {url}")
        