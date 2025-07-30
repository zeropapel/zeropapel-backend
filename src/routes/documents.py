import os
import uuid
import hashlib
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from src.models.user import User, Document, DocumentField, db
from src.routes.auth import log_action

documents_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(file_path):
    """Get file MIME type"""
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except:
        return None

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def log_action(action_type, user_id=None, document_id=None, details=None, ip_address=None):
    """Log user actions for audit trail"""
    log = AuditLog(
        action_type=action_type,
        user_id=user_id,
        document_id=document_id,
        details=details,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()

def convert_docx_to_pdf(docx_path, pdf_path):
    """Convert DOCX to PDF (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In production, you would use a library like python-docx + reportlab
        # or a service like LibreOffice headless mode
        
        # For now, we'll just copy the file and rename it
        # This is NOT a real conversion - just for demonstration
        import shutil
        shutil.copy2(docx_path, pdf_path)
        
        current_app.logger.warning(f"DOCX to PDF conversion is not implemented. File copied: {docx_path} -> {pdf_path}")
        return True
    except Exception as e:
        current_app.logger.error(f"DOCX to PDF conversion error: {str(e)}")
        return False

@documents_bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    """Get user's documents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters for filtering and pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        # Build query
        query = Document.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if search:
            query = query.filter(Document.filename.contains(search))
        
        # Order by creation date (newest first)
        query = query.order_by(Document.created_at.desc())
        
        # Paginate
        documents = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'documents': [doc.to_dict() for doc in documents.items],
            'total': documents.total,
            'pages': documents.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get documents error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a new document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only PDF, DOC, and DOCX files are supported'}), 400
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Verify file type
        file_type = get_file_type(file_path)
        if not file_type:
            os.remove(file_path)
            return jsonify({'error': 'Could not determine file type'}), 400
        
        # Convert DOCX to PDF if necessary
        final_path = file_path
        if ext.lower() in ['.docx', '.doc']:
            pdf_filename = f"{name}_{uuid.uuid4().hex}.pdf"
            pdf_path = os.path.join(upload_folder, pdf_filename)
            
            if convert_docx_to_pdf(file_path, pdf_path):
                final_path = pdf_path
                # Keep original file for reference
            else:
                os.remove(file_path)
                return jsonify({'error': 'Failed to convert document to PDF'}), 500
        
        # Calculate file hash
        file_hash = calculate_file_hash(final_path)
        
        # Create document record
        document = Document(
            user_id=current_user_id,
            filename=filename,
            original_path=final_path,
            sha256_hash=file_hash
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Log document upload
        log_action(
            'document_uploaded', 
            user_id=current_user_id, 
            document_id=document.id,
            details=f'Uploaded: {filename}',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get specific document details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Get document fields
        fields = DocumentField.query.filter_by(document_id=document_id).all()
        
        # Log document access
        log_action(
            'document_accessed', 
            user_id=current_user_id, 
            document_id=document_id,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'document': document.to_dict(),
            'fields': [field.to_dict() for field in fields]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<int:document_id>/fields', methods=['POST'])
@jwt_required()
def add_document_fields(document_id):
    """Add fields to document (for drag-and-drop editor)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        data = request.get_json()
        if not data or 'fields' not in data:
            return jsonify({'error': 'Fields data is required'}), 400
        
        # Clear existing fields
        DocumentField.query.filter_by(document_id=document_id).delete()
        
        # Add new fields
        for field_data in data['fields']:
            field = DocumentField(
                document_id=document_id,
                field_type=field_data['field_type'],
                page_number=field_data['page_number'],
                x_coord=field_data['x_coord'],
                y_coord=field_data['y_coord'],
                width=field_data.get('width'),
                height=field_data.get('height')
            )
            db.session.add(field)
        
        db.session.commit()
        
        # Log field update
        log_action(
            'document_fields_updated', 
            user_id=current_user_id, 
            document_id=document_id,
            details=f'Added {len(data["fields"])} fields',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Document fields updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Add document fields error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<int:document_id>/download', methods=['GET'])
@jwt_required()
def download_document(document_id):
    """Download document file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Determine which file to serve (signed version if available)
        file_path = document.signed_path if document.signed_path else document.original_path
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        # Log document download
        log_action(
            'document_downloaded', 
            user_id=current_user_id, 
            document_id=document_id,
            ip_address=request.remote_addr
        )
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=document.filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Download document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check if document can be deleted (not signed)
        if document.status == 'signed':
            return jsonify({'error': 'Cannot delete signed documents'}), 400
        
        # Delete files from disk
        try:
            if document.original_path and os.path.exists(document.original_path):
                os.remove(document.original_path)
            if document.signed_path and os.path.exists(document.signed_path):
                os.remove(document.signed_path)
        except Exception as e:
            current_app.logger.warning(f"Could not delete files for document {document_id}: {str(e)}")
        
        # Log document deletion
        log_action(
            'document_deleted', 
            user_id=current_user_id, 
            document_id=document_id,
            details=f'Deleted: {document.filename}',
            ip_address=request.remote_addr
        )
        
        # Delete document record (cascade will handle related records)
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@documents_bp.route('/documents/<int:document_id>/preview', methods=['GET'])
@jwt_required()
def preview_document(document_id):
    """Get document for preview (serve file directly)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        file_path = document.original_path
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        # Log document preview
        log_action(
            'document_previewed', 
            user_id=current_user_id, 
            document_id=document_id,
            ip_address=request.remote_addr
        )
        
        return send_file(file_path)
        
    except Exception as e:
        current_app.logger.error(f"Preview document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

