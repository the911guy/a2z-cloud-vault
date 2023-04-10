from vault import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    file = db.relationship('FileTable', backref='author', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
        

class FileTable(db.Model):
    __tablename__ = 'USER_FILES'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100))
    file = db.Column(db.LargeBinary)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)


    def __init__(self, name, file,user_id):
        self.name = name
        self.file = file
        self.user_id=user_id


    def __repr__(self):
        return f'FILE ID: {self.id} \n FILE NAME: {self.name} \n FILE TAG: {self.tag} \n'
    
db.create_all()    