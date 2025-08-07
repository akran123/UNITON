from fastapi import APIRouter,Depends,Query, HTTPException
from models.user import Guardian, ProtectedPerson
from sqlalchemy.orm import Session
from database import get_db
from schemas.user import GuardianBase,ProtectedPersonBase

router = APIRouter(prefix="/user",tags=["users"])

@router.post("/create/guardian",response_model=GuardianBase)
def create_gardian(guardian_data : GuardianBase, db : Session = Depends(get_db)) :
    query = db.query(Guardian).filter(Guardian.name == guardian_data.name).first()
    if query :
        raise HTTPException(status_code=404)
    
    new_data = Guardian(**guardian_data.model_dump())
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

@router.post("/create/pp",response_model=ProtectedPersonBase)
def create_protectedPerson(guardian_id :int,protectedperson_data : ProtectedPersonBase, db : Session = Depends(get_db)) :
    query = db.query(ProtectedPerson).filter(ProtectedPerson.name == protectedperson_data.name).first()
    if query :
        raise HTTPException(status_code=404)
    
    new_data = ProtectedPerson(**protectedperson_data.model_dump())
    new_data.guardian_id = guardian_id
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data