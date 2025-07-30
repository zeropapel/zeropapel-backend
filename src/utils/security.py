import hashlib
import hmac
import secrets
import time
from datetime import datetime
import requests
from flask import current_app

def calculate_sha256(file_path):
    """Calculate SHA-256 hash of a file"""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        current_app.logger.error(f"Error calculating SHA-256: {str(e)}")
        return None

def generate_timestamp():
    """Generate RFC 3161 compatible timestamp (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In production, you would use a proper TSA (Time Stamping Authority)
        # like FreeTSA or a commercial provider
        
        timestamp_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'unix_timestamp': int(time.time()),
            'source': 'internal',  # In production, this would be the TSA
            'algorithm': 'SHA-256'
        }
        
        current_app.logger.warning("Using placeholder timestamp. Implement proper RFC 3161 TSA in production.")
        
        return timestamp_data
        
    except Exception as e:
        current_app.logger.error(f"Error generating timestamp: {str(e)}")
        return None

def verify_timestamp(timestamp_data):
    """Verify timestamp authenticity (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In production, you would verify against the TSA
        
        if not timestamp_data or 'timestamp' not in timestamp_data:
            return False
        
        # Basic validation - check if timestamp is reasonable
        try:
            timestamp_dt = datetime.fromisoformat(timestamp_data['timestamp'].replace('Z', '+00:00'))
            now = datetime.utcnow()
            
            # Timestamp should not be in the future
            if timestamp_dt > now:
                return False
            
            # Timestamp should not be too old (adjust as needed)
            age_days = (now - timestamp_dt.replace(tzinfo=None)).days
            if age_days > 365 * 10:  # 10 years
                return False
            
            return True
            
        except Exception:
            return False
        
    except Exception as e:
        current_app.logger.error(f"Error verifying timestamp: {str(e)}")
        return False

def generate_secure_token(length=32):
    """Generate a cryptographically secure random token"""
    return secrets.token_urlsafe(length)

def generate_signature_id():
    """Generate a unique signature ID"""
    return f"SIG_{int(time.time())}_{secrets.token_hex(8)}"

def create_signature_hash(document_hash, signer_email, timestamp):
    """Create a signature hash for integrity verification"""
    try:
        data = f"{document_hash}:{signer_email}:{timestamp}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    except Exception as e:
        current_app.logger.error(f"Error creating signature hash: {str(e)}")
        return None

def verify_signature_hash(signature_hash, document_hash, signer_email, timestamp):
    """Verify signature hash integrity"""
    try:
        expected_hash = create_signature_hash(document_hash, signer_email, timestamp)
        return hmac.compare_digest(signature_hash, expected_hash) if expected_hash else False
    except Exception as e:
        current_app.logger.error(f"Error verifying signature hash: {str(e)}")
        return False

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    import re
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename

def validate_ip_address(ip):
    """Validate IP address format"""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def get_client_ip(request):
    """Get client IP address from request, considering proxies"""
    # Check for forwarded IP first (in case of proxy/load balancer)
    forwarded_ips = request.headers.get('X-Forwarded-For')
    if forwarded_ips:
        # Take the first IP in the chain
        ip = forwarded_ips.split(',')[0].strip()
        if validate_ip_address(ip):
            return ip
    
    # Check other common headers
    real_ip = request.headers.get('X-Real-IP')
    if real_ip and validate_ip_address(real_ip):
        return real_ip
    
    # Fall back to remote_addr
    return request.remote_addr

def encrypt_sensitive_data(data, key=None):
    """Encrypt sensitive data (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In production, use proper encryption like Fernet from cryptography library
        
        if key is None:
            key = current_app.config.get('SECRET_KEY', 'default-key')
        
        # For now, just return base64 encoded data with a prefix
        import base64
        encoded = base64.b64encode(data.encode('utf-8')).decode('utf-8')
        return f"ENC:{encoded}"
        
    except Exception as e:
        current_app.logger.error(f"Error encrypting data: {str(e)}")
        return None

def decrypt_sensitive_data(encrypted_data, key=None):
    """Decrypt sensitive data (placeholder implementation)"""
    try:
        # This is a placeholder implementation
        # In production, use proper decryption like Fernet from cryptography library
        
        if not encrypted_data or not encrypted_data.startswith('ENC:'):
            return encrypted_data
        
        if key is None:
            key = current_app.config.get('SECRET_KEY', 'default-key')
        
        # Remove prefix and decode
        import base64
        encoded_data = encrypted_data[4:]  # Remove 'ENC:' prefix
        decoded = base64.b64decode(encoded_data).decode('utf-8')
        return decoded
        
    except Exception as e:
        current_app.logger.error(f"Error decrypting data: {str(e)}")
        return encrypted_data  # Return as-is if decryption fails

