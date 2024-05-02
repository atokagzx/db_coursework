import alchemy_contrib as am  # alchemy models
from sqlalchemy import exc as sqlalchemy_exc

from fastapi import APIRouter, Depends, HTTPException, status, Form
import pydantic_contrib as pm  # pydantic models
from mongo_contrib import MongoFacade


from configure import *
import typing

router = APIRouter()


@router.post("/material/{module_id}", response_model=pm.MaterialFull, tags=["material"])
def create_material(module_id: int,
                    content_type: pm.MaterialContentType,
                    user: dict = UserDependency,
                    db_session = Depends(DBFacade().db_session)):
    '''
    Creates mock material for a module.
    '''
    # check if user is an admin
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can create material")
    # check if module exists
    module = db_session.query(am.Module).filter(am.Module.module_id == module_id).first()
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    if module.course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and course creators can create material")
    material_url = MongoFacade().create_material(None)
    new_material = am.Material(module_id=module_id,
                            content_type=content_type,
                            content=MongoFacade().get_materials(material_url),
                            url=material_url)
    db_session.add(new_material)
    try:
        db_session.commit()
    except sqlalchemy_exc.SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    db_session.refresh(new_material)
    return pm.MaterialFull(material_id=new_material.material_id,
                           module_id=new_material.module_id,
                           content_type=new_material.content_type,
                           content=new_material.content,
                           url=new_material.url)


@router.get("/material/{module_id}", response_model=typing.List[pm.MaterialFull], tags=["material"])
def get_material(module_id: int,
                 user: dict = UserDependency,
                 db_session = Depends(DBFacade().db_session)):
    '''
    Get all material for a module.
    '''
    materials = db_session.query(am.Material).filter(am.Material.module_id == module_id).all()
    materials_response = []
    for material in materials:
        content = MongoFacade().get_materials(material.url)
        materials_response.append(pm.MaterialFull(material_id=material.material_id,
                                                   module_id=material.module_id,
                                                   content_type=material.content_type,
                                                   content=content,
                                                   url=material.url))
    return materials_response
        

@router.patch("/material/{material_id}", response_model=pm.MaterialFull, tags=["material"])
def update_material(material_id: int,
                    content: str = Form(..., description="Material content"),
                    user: dict = UserDependency,
                    db_session = Depends(DBFacade().db_session)):
    '''
    Update material content.
    '''
    # check if user is an admin
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can update material")
    # check if material exists
    material = db_session.query(am.Material).filter(am.Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    if material.module.course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and course creators can update material")
    logger.info(f'updating material {material_id} with url {material.url}')
    MongoFacade().update_material(material.url, content)
    
    return pm.MaterialFull(material_id=material.material_id,
                            module_id=material.module_id,
                            content_type=material.content_type,
                            content=content,
                            url=material.url)


@router.delete("/material/{material_id}", response_model=pm.MaterialFull, tags=["material"])
def delete_material(material_id: int,
                    user: dict = UserDependency,
                    db_session = Depends(DBFacade().db_session)):
    '''
    Delete material.
    '''
    # check if user is an admin
    if "admin" not in user["roles"] and "instructor" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and instructors can delete material")
    # check if creator is the user or an admin
    # check if material exists
    material = db_session.query(am.Material).filter(am.Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")
    if material.module.course.created_by != user["user_id"] and "admin" not in user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins and course creators can delete material")
    logger.info(f'deleting material {material_id} with url {material.url}')
    MongoFacade().delete_material(material.url)
    db_session.delete(material)
    db_session.commit()
    return pm.MaterialFull(material_id=material.material_id,
                           module_id=material.module_id,
                           content_type=material.content_type,
                           content=material.content,
                           url=material.url)
