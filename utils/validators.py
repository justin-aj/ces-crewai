import re
from typing import List, Dict, Tuple
from email_validator import validate_email, EmailNotValidError


def validate_email_address(email: str) -> Tuple[bool, str]:
    """Validate single email address"""
    try:
        # Validate email
        validation = validate_email(email, check_deliverability=False)
        return True, validation.email
    except EmailNotValidError as e:
        return False, str(e)


def validate_email_list(emails: List[str]) -> List[Dict[str, str]]:
    """Validate list of email addresses"""
    results = []
    for email in emails:
        is_valid, result = validate_email_address(email)
        results.append({
            'email': email,
            'valid': is_valid,
            'normalized': result if is_valid else None,
            'error': result if not is_valid else None
        })
    return results


def validate_prospect_data(prospect: Dict) -> Dict[str, List[str]]:
    """Validate all required fields for a prospect"""
    errors = []
    warnings = []

    # Required fields
    required_fields = ['email', 'name', 'position', 'job_description']
    for field in required_fields:
        if field not in prospect or not prospect[field]:
            errors.append(f"Missing required field: {field}")

    # Validate email if present
    if 'email' in prospect and prospect['email']:
        is_valid, _ = validate_email_address(prospect['email'])
        if not is_valid:
            errors.append(f"Invalid email address: {prospect['email']}")

    # Check name format
    if 'name' in prospect and prospect['name']:
        if len(prospect['name'].split()) < 2:
            warnings.append("Name appears to be incomplete (no last name)")

    # Check job description length
    if 'job_description' in prospect and prospect['job_description']:
        if len(prospect['job_description']) < 50:
            warnings.append("Job description seems too short for proper personalization")

    # Optional but recommended fields
    if 'company' not in prospect or not prospect['company']:
        warnings.append("Company name missing - personalization will be limited")

    return {
        'errors': errors,
        'warnings': warnings,
        'valid': len(errors) == 0
    }


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple spaces and trim
    filename = re.sub(r'\s+', '_', filename).strip()
    # Limit length
    return filename[:100]