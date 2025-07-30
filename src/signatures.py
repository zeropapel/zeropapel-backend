from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, Document, SignatureRequest, AuditLog, db
from src.utils.pdf_utils_simple import add_signature_to_pdf, generate_qr_code
from src.utils.security import calculate_sha256, generate_timestamp
import os
from datetime import datetime
import uuid

signatures_bp = Blueprint('signatures', __name__)

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

@signatures_bp.route('/documents/<int:document_id>/signature-requests', methods=['POST'])
@jwt_required()
def create_signature_request(document_id):
    """Create a signature request for a document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        signer_email = data.get('signer_email', '').strip().lower()
        signature_type = data.get('signature_type', 'electronic')
        
        if not signer_email:
            return jsonify({'error': 'Signer email is required'}), 400
        
        if signature_type not in ['electronic', 'digital']:
            return jsonify({'error': 'Invalid signature type'}), 400
        
        # Create signature request
        signature_request = SignatureRequest(
            document_id=document_id,
            signer_email=signer_email,
            signature_type=signature_type
        )
        
        db.session.add(signature_request)
        
        # Update document status
        document.status = 'pending'
        
        db.session.commit()
        
        # Log signature request creation
        log_action(
            'signature_request_created',
            user_id=current_user_id,
            document_id=document_id,
            details=f'Signature request sent to {signer_email} ({signature_type})',
            ip_address=request.remote_addr
        )
        
        # TODO: Send email/WhatsApp notification to signer
        
        return jsonify({
            'message': 'Signature request created successfully',
            'signature_request': signature_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create signature request error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@signatures_bp.route('/signature-requests/<int:request_id>/sign', methods=['POST'])
def sign_document(request_id):
    """Sign a document (electronic signature)"""
    try:
        signature_request = SignatureRequest.query.get(request_id)
        
        if not signature_request:
            return jsonify({'error': 'Signature request not found'}), 404
        
        if signature_request.status != 'pending':
            return jsonify({'error': 'Signature request is not pending'}), 400
        
        document = signature_request.document
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get signature data
        ip_address = request.remote_addr
        geolocation = data.get('geolocation', '')
        biometric_data = data.get('biometric_data', '')  # Placeholder for future biometric integration
        
        # Check if user can sign (freemium logic)
        signer = User.query.filter_by(email=signature_request.signer_email).first()
        if signer and not signer.can_sign_document():
            return jsonify({'error': 'Free document limit exceeded. Please upgrade to continue signing.'}), 403
        
        # Process electronic signature
        if signature_request.signature_type == 'electronic':
            # Generate signed PDF with signature footer and QR code
            signed_pdf_path = process_electronic_signature(document, signature_request, ip_address, geolocation)
            
            if not signed_pdf_path:
                return jsonify({'error': 'Failed to process signature'}), 500
            
            # Update signature request
            signature_request.status = 'signed'
            signature_request.signed_at = datetime.utcnow()
            signature_request.ip_address = ip_address
            signature_request.geolocation = geolocation
            signature_request.biometric_data_placeholder = biometric_data
            
            # Update document
            document.status = 'signed'
            document.signed_path = signed_pdf_path
            document.sha256_hash = calculate_sha256(signed_pdf_path)
            
            # Increment signed documents count for signer
            if signer:
                signer.increment_signed_documents()
            
            db.session.commit()
            
            # Log signature completion
            log_action(
                'document_signed_electronic',
                user_id=signer.id if signer else None,
                document_id=document.id,
                details=f'Electronic signature by {signature_request.signer_email}',
                ip_address=ip_address
            )
            
            return jsonify({
                'message': 'Document signed successfully',
                'signature_request': signature_request.to_dict(),
                'verification_url': url_for('signatures.verify_document', document_id=document.id, _external=True)
            }), 200
            
        elif signature_request.signature_type == 'digital':
            # Placeholder for ICP-Brasil digital signature
            return jsonify({'error': 'Digital signature not implemented yet'}), 501
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Sign document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def process_electronic_signature(document, signature_request, ip_address, geolocation):
    """Process electronic signature and generate signed PDF"""
    try:
        # Generate unique filename for signed document
        name, ext = os.path.splitext(document.filename)
        signed_filename = f"{name}_signed_{uuid.uuid4().hex}{ext}"
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        signed_path = os.path.join(upload_folder, signed_filename)
        
        # Generate signature data
        signature_data = {
            'signer_email': signature_request.signer_email,
            'signed_at': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'geolocation': geolocation,
            'signature_id': str(uuid.uuid4()),
            'document_id': document.id
        }
        
        # Generate QR code for verification
        verification_url = url_for('signatures.verify_document', document_id=document.id, _external=True)
        qr_code_path = generate_qr_code(verification_url)
        
        # Add signature footer and QR code to PDF
        success = add_signature_to_pdf(
            document.original_path,
            signed_path,
            signature_data,
            qr_code_path
        )
        
        # Clean up temporary QR code file
        if qr_code_path and os.path.exists(qr_code_path):
            os.remove(qr_code_path)
        
        if success:
            return signed_path
        else:
            return None
            
    except Exception as e:
        current_app.logger.error(f"Process electronic signature error: {str(e)}")
        return None

@signatures_bp.route('/signature-requests/<int:request_id>', methods=['GET'])
def get_signature_request(request_id):
    """Get signature request details (for signing page)"""
    try:
        signature_request = SignatureRequest.query.get(request_id)
        
        if not signature_request:
            return jsonify({'error': 'Signature request not found'}), 404
        
        document = signature_request.document
        
        return jsonify({
            'signature_request': signature_request.to_dict(),
            'document': {
                'id': document.id,
                'filename': document.filename,
                'status': document.status
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get signature request error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@signatures_bp.route('/documents/<int:document_id>/verify', methods=['GET'])
def verify_document(document_id):
    """Public endpoint to verify document authenticity"""
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        if document.status != 'signed':
            return jsonify({'error': 'Document is not signed'}), 400
        
        # Get signature requests for this document
        signature_requests = SignatureRequest.query.filter_by(
            document_id=document_id,
            status='signed'
        ).all()
        
        # Get audit logs for this document
        audit_logs = AuditLog.query.filter_by(document_id=document_id).order_by(AuditLog.timestamp.desc()).all()
        
        # Verify file integrity if signed file exists
        file_integrity = False
        if document.signed_path and os.path.exists(document.signed_path):
            current_hash = calculate_sha256(document.signed_path)
            file_integrity = (current_hash == document.sha256_hash)
        
        verification_data = {
            'document': {
                'id': document.id,
                'filename': document.filename,
                'status': document.status,
                'sha256_hash': document.sha256_hash,
                'created_at': document.created_at.isoformat() if document.created_at else None,
                'updated_at': document.updated_at.isoformat() if document.updated_at else None
            },
            'signatures': [req.to_dict() for req in signature_requests],
            'audit_trail': [log.to_dict() for log in audit_logs],
            'file_integrity': file_integrity,
            'verification_timestamp': datetime.utcnow().isoformat()
        }
        
        # Log verification access
        log_action(
            'document_verification_accessed',
            document_id=document_id,
            details='Public verification accessed',
            ip_address=request.remote_addr
        )
        
        return jsonify(verification_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Verify document error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@signatures_bp.route('/documents/<int:document_id>/signature-requests', methods=['GET'])
@jwt_required()
def get_document_signature_requests(document_id):
    """Get all signature requests for a document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        signature_requests = SignatureRequest.query.filter_by(document_id=document_id).all()
        
        return jsonify({
            'signature_requests': [req.to_dict() for req in signature_requests]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get document signature requests error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@signatures_bp.route('/signature-requests/<int:request_id>/resend', methods=['POST'])
@jwt_required()
def resend_signature_request(request_id):
    """Resend signature request notification"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        signature_request = SignatureRequest.query.get(request_id)
        
        if not signature_request:
            return jsonify({'error': 'Signature request not found'}), 404
        
        # Check if user owns the document
        document = signature_request.document
        if document.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if signature_request.status != 'pending':
            return jsonify({'error': 'Can only resend pending signature requests'}), 400
        
        # Update sent timestamp
        signature_request.sent_at = datetime.utcnow()
        db.session.commit()
        
        # Log resend action
        log_action(
            'signature_request_resent',
            user_id=current_user_id,
            document_id=document.id,
            details=f'Signature request resent to {signature_request.signer_email}',
            ip_address=request.remote_addr
        )
        
        # TODO: Send email/WhatsApp notification to signer
        
        return jsonify({
            'message': 'Signature request resent successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Resend signature request error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@signatures_bp.route('/signature-requests/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_signature_request(request_id):
    """Cancel a signature request"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        signature_request = SignatureRequest.query.get(request_id)
        
        if not signature_request:
            return jsonify({'error': 'Signature request not found'}), 404
        
        # Check if user owns the document
        document = signature_request.document
        if document.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if signature_request.status != 'pending':
            return jsonify({'error': 'Can only cancel pending signature requests'}), 400
        
        # Update status
        signature_request.status = 'rejected'
        
        # Check if there are other pending requests for this document
        other_pending = SignatureRequest.query.filter_by(
            document_id=document.id,
            status='pending'
        ).filter(SignatureRequest.id != request_id).first()
        
        if not other_pending:
            document.status = 'uploaded'  # Reset document status if no pending requests
        
        db.session.commit()
        
        # Log cancellation
        log_action(
            'signature_request_cancelled',
            user_id=current_user_id,
            document_id=document.id,
            details=f'Signature request cancelled for {signature_request.signer_email}',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Signature request cancelled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Cancel signature request error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

