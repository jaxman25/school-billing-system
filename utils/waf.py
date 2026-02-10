import re
from flask import request, abort
from functools import wraps
import time

class WebApplicationFirewall:
    def __init__(self):
        self.request_log = []
        self.blocked_ips = set()
        
        # Common attack patterns
        self.sql_injection_patterns = [
            r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
            r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
            r"((\%27)|(\'))union",
            r"exec(\s|\+)+(s|x)p\w+",
        ]
        
        self.xss_patterns = [
            r"((\%3C)|<)((\%2F)|\/)*[a-z0-9\%]+((\%3E)|>)",
            r"((\%3C)|<)((\%69)|i|(\%49))((\%6D)|m|(\%4D))((\%67)|g|(\%47))[^\n]+((\%3E)|>)",
            r"((\%3C)|<)[^\n]+((\%3E)|>)",
        ]
        
        self.path_traversal_patterns = [
            r"\.\.\/",
            r"\.\.\\",
            r"\/etc\/",
            r"\/windows\/",
        ]
    
    def check_request(self, request):
        """Check incoming request for attacks"""
        
        # Check blocked IPs
        client_ip = request.remote_addr
        if client_ip in self.blocked_ips:
            return False, "IP blocked"
        
        # Check request path
        if self._check_path_traversal(request.path):
            self.blocked_ips.add(client_ip)
            return False, "Path traversal attempt"
        
        # Check GET parameters
        for key, value in request.args.items():
            if self._check_sql_injection(value) or self._check_xss(value):
                self.blocked_ips.add(client_ip)
                return False, f"Attack detected in parameter: {key}"
        
        # Check POST data
        if request.method == "POST":
            for key, value in request.form.items():
                if self._check_sql_injection(value) or self._check_xss(value):
                    self.blocked_ips.add(client_ip)
                    return False, f"Attack detected in form field: {key}"
        
        # Check headers
        user_agent = request.headers.get('User-Agent', '')
        if self._check_sql_injection(user_agent) or self._check_xss(user_agent):
            self.blocked_ips.add(client_ip)
            return False, "Malicious User-Agent"
        
        # Log request
        self._log_request(request)
        
        return True, "Request allowed"
    
    def _check_sql_injection(self, input_string):
        for pattern in self.sql_injection_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return True
        return False
    
    def _check_xss(self, input_string):
        for pattern in self.xss_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return True
        return False
    
    def _check_path_traversal(self, path):
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True
        return False
    
    def _log_request(self, request):
        log_entry = {
            'timestamp': time.time(),
            'ip': request.remote_addr,
            'method': request.method,
            'path': request.path,
            'user_agent': request.headers.get('User-Agent', ''),
            'status': 'allowed'
        }
        self.request_log.append(log_entry)
        
        # Keep only last 1000 logs
        if len(self.request_log) > 1000:
            self.request_log = self.request_log[-1000:]
    
    def get_blocked_ips(self):
        return list(self.blocked_ips)
    
    def unblock_ip(self, ip):
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            return True
        return False
    
    def get_request_logs(self, limit=100):
        return self.request_log[-limit:]

# Global WAF instance
waf = WebApplicationFirewall()

# Decorator to protect routes
def waf_protect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        allowed, reason = waf.check_request(request)
        if not allowed:
            # Log the attempt
            print(f" WAF Blocked: {request.remote_addr} - {reason}")
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# WAF admin routes (protected)
def setup_waf_routes(app):
    @app.route('/admin/waf/blocked', methods=['GET'])
    @admin_required
    def waf_blocked_ips():
        from flask import jsonify
        return jsonify({'blocked_ips': waf.get_blocked_ips()})
    
    @app.route('/admin/waf/unblock/<ip>', methods=['POST'])
    @admin_required
    def waf_unblock_ip(ip):
        if waf.unblock_ip(ip):
            return jsonify({'success': True, 'message': f'IP {ip} unblocked'})
        return jsonify({'success': False, 'message': 'IP not found'}), 404
    
    @app.route('/admin/waf/logs', methods=['GET'])
    @admin_required
    def waf_logs():
        limit = request.args.get('limit', 100, type=int)
        return jsonify({'logs': waf.get_request_logs(limit)})
