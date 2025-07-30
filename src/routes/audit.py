from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, Document, AuditLog, SignatureRequest, db
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, desc

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit/logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Get audit logs (admin only or user's own logs)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        action_type = request.args.get('action_type')
        document_id = request.args.get('document_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build base query
        if user.is_admin:
            # Admin can see all logs
            query = AuditLog.query
        else:
            # Regular users can only see their own logs
            query = AuditLog.query.filter(
                or_(
                    AuditLog.user_id == current_user_id,
                    AuditLog.document_id.in_(
                        db.session.query(Document.id).filter_by(user_id=current_user_id)
                    )
                )
            )
        
        # Apply filters
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        
        if document_id:
            # Check if user has access to this document
            if not user.is_admin:
                document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
                if not document:
                    return jsonify({'error': 'Document not found or access denied'}), 404
            
            query = query.filter(AuditLog.document_id == document_id)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format.'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(AuditLog.timestamp <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format.'}), 400
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Paginate
        logs = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get audit logs error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@audit_bp.route('/audit/logs/<int:log_id>', methods=['GET'])
@jwt_required()
def get_audit_log(log_id):
    """Get specific audit log details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        log = AuditLog.query.get(log_id)
        
        if not log:
            return jsonify({'error': 'Audit log not found'}), 404
        
        # Check access permissions
        if not user.is_admin:
            # Regular users can only see logs related to their documents or actions
            if log.user_id != current_user_id:
                if log.document_id:
                    document = Document.query.filter_by(id=log.document_id, user_id=current_user_id).first()
                    if not document:
                        return jsonify({'error': 'Access denied'}), 403
                else:
                    return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'log': log.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get audit log error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@audit_bp.route('/audit/stats', methods=['GET'])
@jwt_required()
def get_audit_stats():
    """Get audit statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date range for stats
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build base query based on user permissions
        if user.is_admin:
            base_query = AuditLog.query
            document_query = Document.query
            signature_query = SignatureRequest.query
        else:
            base_query = AuditLog.query.filter(
                or_(
                    AuditLog.user_id == current_user_id,
                    AuditLog.document_id.in_(
                        db.session.query(Document.id).filter_by(user_id=current_user_id)
                    )
                )
            )
            document_query = Document.query.filter_by(user_id=current_user_id)
            signature_query = SignatureRequest.query.join(Document).filter(Document.user_id == current_user_id)
        
        # Filter by date range
        logs_in_period = base_query.filter(AuditLog.timestamp >= start_date)
        
        # Calculate statistics
        stats = {
            'period_days': days,
            'total_logs': logs_in_period.count(),
            'total_documents': document_query.count(),
            'documents_uploaded': document_query.filter(Document.created_at >= start_date).count(),
            'documents_signed': document_query.filter(
                and_(Document.status == 'signed', Document.updated_at >= start_date)
            ).count(),
            'signature_requests_sent': signature_query.filter(SignatureRequest.sent_at >= start_date).count(),
            'signature_requests_completed': signature_query.filter(
                and_(SignatureRequest.status == 'signed', SignatureRequest.signed_at >= start_date)
            ).count(),
            'action_types': {}
        }
        
        # Get action type breakdown
        action_counts = db.session.query(
            AuditLog.action_type,
            db.func.count(AuditLog.id)
        ).filter(
            AuditLog.timestamp >= start_date
        )
        
        if not user.is_admin:
            action_counts = action_counts.filter(
                or_(
                    AuditLog.user_id == current_user_id,
                    AuditLog.document_id.in_(
                        db.session.query(Document.id).filter_by(user_id=current_user_id)
                    )
                )
            )
        
        action_counts = action_counts.group_by(AuditLog.action_type).all()
        
        for action_type, count in action_counts:
            stats['action_types'][action_type] = count
        
        # Get daily activity for the period
        daily_activity = db.session.query(
            db.func.date(AuditLog.timestamp).label('date'),
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date
        )
        
        if not user.is_admin:
            daily_activity = daily_activity.filter(
                or_(
                    AuditLog.user_id == current_user_id,
                    AuditLog.document_id.in_(
                        db.session.query(Document.id).filter_by(user_id=current_user_id)
                    )
                )
            )
        
        daily_activity = daily_activity.group_by(
            db.func.date(AuditLog.timestamp)
        ).order_by('date').all()
        
        stats['daily_activity'] = [
            {
                'date': str(date),
                'count': count
            }
            for date, count in daily_activity
        ]
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Get audit stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@audit_bp.route('/audit/export', methods=['GET'])
@jwt_required()
def export_audit_logs():
    """Export audit logs to CSV"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        action_type = request.args.get('action_type')
        
        # Build query
        if user.is_admin:
            query = AuditLog.query
        else:
            query = AuditLog.query.filter(
                or_(
                    AuditLog.user_id == current_user_id,
                    AuditLog.document_id.in_(
                        db.session.query(Document.id).filter_by(user_id=current_user_id)
                    )
                )
            )
        
        # Apply filters
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(AuditLog.timestamp <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        
        # Order by timestamp
        logs = query.order_by(desc(AuditLog.timestamp)).all()
        
        # Convert to CSV format
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Timestamp', 'Action Type', 'User ID', 'Document ID',
            'IP Address', 'Details'
        ])
        
        # Write data
        for log in logs:
            writer.writerow([
                log.id,
                log.timestamp.isoformat() if log.timestamp else '',
                log.action_type,
                log.user_id,
                log.document_id,
                log.ip_address,
                log.details
            ])
        
        output.seek(0)
        csv_data = output.getvalue()
        
        # Return CSV data
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=audit_logs_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
        
    except Exception as e:
        current_app.logger.error(f"Export audit logs error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@audit_bp.route('/audit/document/<int:document_id>/timeline', methods=['GET'])
@jwt_required()
def get_document_timeline(document_id):
    """Get complete timeline for a specific document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check document access
        if not user.is_admin:
            document = Document.query.filter_by(id=document_id, user_id=current_user_id).first()
            if not document:
                return jsonify({'error': 'Document not found or access denied'}), 404
        else:
            document = Document.query.get(document_id)
            if not document:
                return jsonify({'error': 'Document not found'}), 404
        
        # Get all audit logs for this document
        audit_logs = AuditLog.query.filter_by(document_id=document_id).order_by(AuditLog.timestamp).all()
        
        # Get all signature requests for this document
        signature_requests = SignatureRequest.query.filter_by(document_id=document_id).all()
        
        # Build timeline
        timeline = []
        
        # Add audit logs to timeline
        for log in audit_logs:
            timeline.append({
                'type': 'audit_log',
                'timestamp': log.timestamp.isoformat() if log.timestamp else None,
                'action': log.action_type,
                'details': log.details,
                'user_id': log.user_id,
                'ip_address': log.ip_address
            })
        
        # Add signature events to timeline
        for req in signature_requests:
            # Signature request sent
            timeline.append({
                'type': 'signature_request',
                'timestamp': req.sent_at.isoformat() if req.sent_at else None,
                'action': 'signature_request_sent',
                'details': f'Signature request sent to {req.signer_email}',
                'signer_email': req.signer_email,
                'signature_type': req.signature_type
            })
            
            # Signature completed (if applicable)
            if req.signed_at:
                timeline.append({
                    'type': 'signature_completed',
                    'timestamp': req.signed_at.isoformat(),
                    'action': 'document_signed',
                    'details': f'Document signed by {req.signer_email}',
                    'signer_email': req.signer_email,
                    'signature_type': req.signature_type,
                    'ip_address': req.ip_address,
                    'geolocation': req.geolocation
                })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x['timestamp'] or '1970-01-01T00:00:00')
        
        return jsonify({
            'document': document.to_dict(),
            'timeline': timeline
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get document timeline error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@audit_bp.route('/audit/integrity-check', methods=['POST'])
@jwt_required()
def integrity_check():
    """Perform integrity check on documents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        document_ids = data.get('document_ids', []) if data else []
        
        # If no specific documents provided, check all user's documents
        if not document_ids:
            if user.is_admin:
                documents = Document.query.filter(Document.signed_path.isnot(None)).all()
            else:
                documents = Document.query.filter_by(user_id=current_user_id).filter(Document.signed_path.isnot(None)).all()
        else:
            if user.is_admin:
                documents = Document.query.filter(Document.id.in_(document_ids)).all()
            else:
                documents = Document.query.filter(
                    and_(Document.id.in_(document_ids), Document.user_id == current_user_id)
                ).all()
        
        results = []
        
        for document in documents:
            result = {
                'document_id': document.id,
                'filename': document.filename,
                'status': document.status,
                'stored_hash': document.sha256_hash,
                'current_hash': None,
                'integrity_valid': False,
                'file_exists': False,
                'error': None
            }
            
            try:
                # Check if signed file exists
                if document.signed_path and os.path.exists(document.signed_path):
                    result['file_exists'] = True
                    
                    # Calculate current hash
                    from src.utils.security import calculate_sha256
                    current_hash = calculate_sha256(document.signed_path)
                    result['current_hash'] = current_hash
                    
                    # Compare hashes
                    if current_hash and document.sha256_hash:
                        result['integrity_valid'] = (current_hash == document.sha256_hash)
                    
                else:
                    result['error'] = 'Signed file not found'
                
            except Exception as e:
                result['error'] = str(e)
            
            results.append(result)
        
        # Log integrity check
        from src.routes.auth import log_action
        log_action(
            'integrity_check_performed',
            user_id=current_user_id,
            details=f'Integrity check on {len(results)} documents',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'results': results,
            'summary': {
                'total_checked': len(results),
                'valid': sum(1 for r in results if r['integrity_valid']),
                'invalid': sum(1 for r in results if not r['integrity_valid'] and r['file_exists']),
                'missing_files': sum(1 for r in results if not r['file_exists'])
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Integrity check error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

