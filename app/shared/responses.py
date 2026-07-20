from flask import jsonify

def api_response(status: int, message: str, data=None):
    """
    Generate a uniform API response format.
    
    Structure:
    {
        "status": status,
        "message": message,
        "data": data
    }
    """
    return jsonify({
        "status": status,
        "message": message,
        "data": data
    }), status
