from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    oauth_id = db.Column(db.String(255), unique=True, nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    free_documents_signed = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def can_sign_document(self):
        """Check if user can sign more documents (freemium logic)"""
        from config import Config
        if self.is_admin:
            return True
        return self.free_documents_signed < Config.FREE_DOCUMENTS_LIMIT

    def increment_signed_documents(self):
        """Increment the count of signed documents"""
        self.free_documents_signed += 1
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'email_verified': self.email_verified,
            'free_documents_signed': self.free_documents_signed,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_path = db.Column(db.String(255), nullable=False)
    signed_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('uploaded', 'pending', 'signed', 'rejected', name='document_status'), default='uploaded')
    sha256_hash = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    signature_requests = db.relationship('SignatureRequest', backref='document', lazy=True, cascade='all, delete-orphan')
    document_fields = db.relationship('DocumentField', backref='document', lazy=True, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='document', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_path': self.original_path,
            'signed_path': self.signed_path,
            'status': self.status,
            'sha256_hash': self.sha256_hash,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Document {self.filename}>'


class SignatureRequest(db.Model):
    __tablename__ = 'signature_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    signer_email = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('pending', 'signed', 'rejected', name='signature_status'), default='pending')
    signature_type = db.Column(db.Enum('electronic', 'digital', name='signature_type'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    signed_at = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    geolocation = db.Column(db.String(255), nullable=True)
    biometric_data_placeholder = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'signer_email': self.signer_email,
            'status': self.status,
            'signature_type': self.signature_type,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'signed_at': self.signed_at.isoformat() if self.signed_at else None,
            'ip_address': self.ip_address,
            'geolocation': self.geolocation
        }

    def __repr__(self):
        return f'<SignatureRequest {self.signer_email} for Document {self.document_id}>'


class DocumentField(db.Model):
    __tablename__ = 'document_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    field_type = db.Column(db.Enum('signature', 'date', 'full_name', 'checkbox', name='field_type'), nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    x_coord = db.Column(db.Numeric(10, 2), nullable=False)
    y_coord = db.Column(db.Numeric(10, 2), nullable=False)
    width = db.Column(db.Numeric(10, 2), nullable=True)
    height = db.Column(db.Numeric(10, 2), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'field_type': self.field_type,
            'page_number': self.page_number,
            'x_coord': float(self.x_coord),
            'y_coord': float(self.y_coord),
            'width': float(self.width) if self.width else None,
            'height': float(self.height) if self.height else None
        }

    def __repr__(self):
        return f'<DocumentField {self.field_type} at ({self.x_coord}, {self.y_coord})>'


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action_type = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    def __repr__(self):
        return f'<AuditLog {self.action_type} at {self.timestamp}>'


class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(255), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value
        }

    def __repr__(self):
        return f'<Settings {self.setting_key}: {self.setting_value}>'

