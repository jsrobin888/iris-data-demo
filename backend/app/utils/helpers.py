"""
Utility helper functions
"""

import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
import json


def generate_request_id() -> str:
    """Generate a unique request ID"""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"


def hash_string(text: str) -> str:
    """Create SHA256 hash of a string"""
    return hashlib.sha256(text.encode()).hexdigest()


def safe_json_dumps(data: Any) -> str:
    """Safely convert data to JSON string"""
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    return json.dumps(data, default=json_serializer)


def mask_email(email: str) -> str:
    """Mask email address for privacy"""
    parts = email.split('@')
    if len(parts) != 2:
        return "***"
    
    username, domain = parts
    if len(username) <= 3:
        masked_username = "*" * len(username)
    else:
        masked_username = username[:2] + "*" * (len(username) - 3) + username[-1]
    
    return f"{masked_username}@{domain}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def sanitize_dict(data: Dict[str, Any], sensitive_keys: Optional[list] = None) -> Dict[str, Any]:
    """Remove sensitive information from dictionary"""
    if sensitive_keys is None:
        sensitive_keys = ['password', 'token', 'secret', 'api_key']
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, sensitive_keys)
        else:
            sanitized[key] = value
    
    return sanitized