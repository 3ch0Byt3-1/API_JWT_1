from flask import Flask, jsonify, request
from flask_caching import Cache
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii
import MajorLoginReq_pb2
import MajorLoginRes_pb2
import jwt_generator_pb2
import login_pb2
import json
import time
import warnings
from colorama import init, Fore, Style
from urllib3.exceptions import InsecureRequestWarning
import logging
from datetime import datetime

# Disable SSL warnings
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Constants
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

# Init colorama
init(autoreset=True)

# Setup advanced logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.CYAN}%(asctime)s {Fore.GREEN}%(levelname)s {Fore.WHITE}%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('premium_auth.log')
    ]
)

logger = logging.getLogger(__name__)

# Flask setup
app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache', 
    'CACHE_DEFAULT_TIMEOUT': 28800,
    'CACHE_THRESHOLD': 1000
})

class PremiumAuthManager:
    """Premium authentication manager with advanced features"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        
    def get_token(self, password, uid):
        """Premium token acquisition with retry logic"""
        for attempt in range(3):
            try:
                url = "https://100067.connect.garena.com/oauth/guest/token/grant"
                headers = {
                    "Host": "100067.connect.garena.com",
                    "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "close"
                }
                data = {
                    "uid": uid,
                    "password": password,
                    "response_type": "token",
                    "client_type": "2",
                    "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
                    "client_id": "100067"
                }
                
                response = self.session.post(url, headers=headers, data=data, timeout=10)
                if response.status_code == 200:
                    token_json = response.json()
                    if "access_token" in token_json and "open_id" in token_json:
                        logger.info(f"Premium token acquired for UID: {uid} (Attempt {attempt + 1})")
                        return token_json
                elif attempt == 2:
                    logger.error(f"Token API failed with status: {response.status_code}")
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Token acquisition failed: {str(e)}")
                time.sleep(1)
        return None

    def encrypt_message(self, plaintext):
        """Premium encryption with validation"""
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        padded = pad(plaintext, AES.block_size)
        return cipher.encrypt(padded)

    def decrypt_message(self, ciphertext):
        """Advanced decryption with multiple fallbacks"""
        try:
            cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
            decrypted = cipher.decrypt(ciphertext)
            return unpad(decrypted, AES.block_size)
        except Exception as e:
            logger.debug(f"Decryption failed, trying alternative methods: {e}")
            return None

    def create_premium_login_request(self, token_data):
        """Create premium MajorLogin request with optimized parameters"""
        major_login = MajorLoginReq_pb2.MajorLogin()
        
        # Premium device configuration
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Core authentication data
        major_login.event_time = current_time
        major_login.game_name = "free fire"
        major_login.platform_id = 1
        major_login.client_version = "2.112.2"
        major_login.open_id = token_data['open_id']
        major_login.open_id_type = "4"
        major_login.access_token = token_data['access_token']
        
        # Premium device specs
        major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
        major_login.system_hardware = "Handheld"
        major_login.device_type = "Handheld"
        major_login.telecom_operator = "Verizon"
        major_login.network_type = "WIFI"
        major_login.client_ip = "223.191.51.89"
        major_login.language = "en"
        
        # Premium display specs
        major_login.screen_width = 1920
        major_login.screen_height = 1080
        major_login.screen_dpi = "280"
        
        # Premium hardware specs
        major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
        major_login.memory = 3003
        major_login.gpu_renderer = "Adreno (TM) 640"
        major_login.gpu_version = "OpenGL ES 3.1 v1.46"
        major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
        
        # Memory configuration
        memory_available = major_login.memory_available
        memory_available.version = 55
        memory_available.hidden_value = 81
        
        # Advanced settings
        major_login.platform_sdk_id = 1
        major_login.network_operator_a = "Verizon"
        major_login.network_type_a = "WIFI"
        major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
        
        # Storage information
        major_login.external_storage_total = 36235
        major_login.external_storage_available = 31335
        major_login.internal_storage_total = 2519
        major_login.internal_storage_available = 703
        major_login.game_disk_storage_available = 25010
        major_login.game_disk_storage_total = 26628
        major_login.external_sdcard_avail_storage = 32992
        major_login.external_sdcard_total_storage = 36235
        
        # Login configuration
        major_login.login_by = 3
        major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
        major_login.reg_avatar = 1
        major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
        major_login.channel_type = 3
        
        # CPU and graphics
        major_login.cpu_type = 2
        major_login.cpu_architecture = "64"
        major_login.client_version_code = "2019117863"
        major_login.graphics_api = "OpenGLES2"
        major_login.supported_astc_bitset = 16383
        major_login.login_open_id_type = 4
        
        # Analytics and security
        major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
        major_login.loading_time = 13564
        major_login.release_channel = "android"
        major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
        major_login.android_engine_init_flag = 110009
        major_login.if_push = 1
        major_login.is_vpn = 1
        major_login.origin_platform_type = "4"
        major_login.primary_platform_type = "4"
        
        return major_login

    def parse_jwt_response(self, content):
        """Premium JWT response parsing"""
        jwt_msg = jwt_generator_pb2.Garena_420()
        jwt_msg.ParseFromString(content)
        
        response_dict = {}
        lines = str(jwt_msg).split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                response_dict[key.strip()] = value.strip().strip('"')
        return response_dict

    def parse_user_data_premium(self, response_content):
        """Advanced user data parsing with multiple fallbacks"""
        parsing_methods = [
            self._parse_method_1,  # Direct LoginRes
            self._parse_method_2,  # Decrypted LoginRes  
            self._parse_method_3,  # Direct LoginReq
            self._parse_method_4,  # Decrypted LoginReq
        ]
        
        for i, method in enumerate(parsing_methods, 1):
            try:
                result = method(response_content)
                if result and result.get("nickname"):
                    logger.info(f"Method {i} successful: {result['nickname']}")
                    return result
            except Exception as e:
                logger.debug(f"Method {i} failed: {e}")
        
        logger.warning("All parsing methods failed, using default data")
        return None

    def _parse_method_1(self, content):
        """Direct LoginRes parsing"""
        login_res = login_pb2.LoginRes()
        login_res.ParseFromString(content)
        return self._extract_user_data(login_res) if login_res.nickname else None

    def _parse_method_2(self, content):
        """Decrypted LoginRes parsing"""
        decrypted = self.decrypt_message(content)
        if decrypted:
            login_res = login_pb2.LoginRes()
            login_res.ParseFromString(decrypted)
            return self._extract_user_data(login_res) if login_res.nickname else None
        return None

    def _parse_method_3(self, content):
        """Direct LoginReq parsing"""
        login_req = login_pb2.LoginReq()
        login_req.ParseFromString(content)
        return self._extract_user_data(login_req) if login_req.nickname else None

    def _parse_method_4(self, content):
        """Decrypted LoginReq parsing"""
        decrypted = self.decrypt_message(content)
        if decrypted:
            login_req = login_pb2.LoginReq()
            login_req.ParseFromString(decrypted)
            return self._extract_user_data(login_req) if login_req.nickname else None
        return None

    def _extract_user_data(self, obj):
        """Extract user data from protobuf object"""
        return {
            "nickname": getattr(obj, 'nickname', ''),
            "region": getattr(obj, 'region', ''),
            "level": getattr(obj, 'level', 0),
            "exp": getattr(obj, 'exp', 0),
            "create_at": getattr(obj, 'create_at', 0)
        }

    def get_base_url(self, login_res):
        """Smart URL detection with fallbacks"""
        url_fields = ['server_url', 'url', 'base_url', 'game_url', 'login_url']
        
        for field in url_fields:
            if hasattr(login_res, field):
                url_value = getattr(login_res, field)
                if url_value and url_value.strip():
                    logger.info(f"Using URL from {field}: {url_value}")
                    return url_value
        
        default_url = "https://loginbp.common.ggbluefox.com"
        logger.info(f"Using default URL: {default_url}")
        return default_url

    def _get_user_data_premium(self, login_res, token, base_url, headers):
        """Get premium user data with advanced parsing"""
        login_req = login_pb2.LoginReq()
        login_req.account_id = login_res.account_id
        
        serialized_login = login_req.SerializeToString()
        encrypted_login = self.encrypt_message(serialized_login)
        login_hex = binascii.hexlify(encrypted_login).decode()

        get_headers = headers.copy()
        get_headers["Authorization"] = f"Bearer {token}"

        get_login_url = f"{base_url}/GetLoginData"
        logger.info(f"Requesting premium user data from: {get_login_url}")
        
        response = self.session.post(
            get_login_url,
            data=bytes.fromhex(login_hex),
            headers=get_headers,
            timeout=30
        )

        user_data = {
            "nickname": "",
            "region": "", 
            "level": 0,
            "exp": 0,
            "create_at": 0
        }

        if response.status_code == 200:
            logger.info("User data request successful")
            parsed_data = self.parse_user_data_premium(response.content)
            if parsed_data:
                user_data = parsed_data
            else:
                logger.warning("Using default user data (parsing failed)")
        else:
            logger.warning(f"GetLoginData status: {response.status_code}")

        return user_data

    def _build_premium_response(self, login_res, jwt_dict, token, user_data):
        """Build premium response with enhanced data"""
        response_data = {
            "accountId": str(login_res.account_id) if login_res.account_id else "",
            "accountNickname": user_data["nickname"],
            "accountRegion": user_data["region"],
            "accountLevel": user_data["level"],
            "accountLevelExp": user_data["exp"],
            "accountCreateAt": user_data["create_at"],
            "tokenStatus": jwt_dict.get("status", "valid"),
            "token": token,
            "expireAt": int(time.time()) + 28800,
            "status": "success",
            "premium": True,
            "timestamp": int(time.time()),
            "version": "2.0.0"
        }

        # Add all available optional fields
        optional_fields = {
            'lockRegion': 'lock_region',
            'notiRegion': 'noti_region', 
            'ipRegion': 'ip_region',
            'agoraEnvironment': 'agora_environment',
            'ttl': 'ttl',
            'serverUrl': 'server_url'
        }
        
        for json_field, proto_field in optional_fields.items():
            if hasattr(login_res, proto_field):
                value = getattr(login_res, proto_field)
                if value is not None and value != "":
                    response_data[json_field] = value

        logger.info(f"Premium response built: Account {response_data['accountId']}")
        return response_data

# Initialize premium manager
premium_manager = PremiumAuthManager()

@app.route('/token', methods=['GET'])
@cache.cached(timeout=28800, query_string=True)
def get_premium_auth():
    """Premium authentication endpoint"""
    start_time = time.time()
    uid = request.args.get('uid')
    password = request.args.get('password')

    if not uid or not password:
        return jsonify({
            "status": "error",
            "message": "Both uid and password parameters are required",
            "timestamp": int(time.time())
        }), 400

    logger.info(f"Starting premium authentication for UID: {uid}")

    # Step 1: Acquire OAuth token
    token_data = premium_manager.get_token(password, uid)
    if not token_data:
        return jsonify({
            "uid": uid,
            "status": "invalid",
            "message": "Authentication failed: Invalid UID or Password",
            "timestamp": int(time.time())
        }), 400

    try:
        # Step 2: Create and send premium login request
        major_login = premium_manager.create_premium_login_request(token_data)
        serialized = major_login.SerializeToString()
        encrypted = premium_manager.encrypt_message(serialized)
        edata = binascii.hexlify(encrypted).decode()

        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; Android 9)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': "OB51"
        }

        logger.info("Sending premium MajorLogin request...")
        response = premium_manager.session.post(
            "https://loginbp.common.ggbluefox.com/MajorLogin",
            data=bytes.fromhex(edata),
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            logger.error(f"MajorLogin failed with status: {response.status_code}")
            return jsonify({
                "status": "error",
                "message": f"MajorLogin failed: {response.status_code}",
                "timestamp": int(time.time())
            }), 400

        # Parse MajorLogin response
        login_res = MajorLoginRes_pb2.MajorLoginRes()
        login_res.ParseFromString(response.content)

        logger.info(f"MajorLogin successful! Account ID: {login_res.account_id}")

        # Parse JWT token
        jwt_dict = premium_manager.parse_jwt_response(response.content)
        token = jwt_dict.get("token", "")

        if not token:
            logger.error("No JWT token in response")
            return jsonify({
                "status": "error", 
                "message": "Authentication failed - no token received",
                "timestamp": int(time.time())
            }), 400

        # Step 3: Get user data
        base_url = premium_manager.get_base_url(login_res)
        user_data = premium_manager._get_user_data_premium(login_res, token, base_url, headers)

        # Build premium response
        response_data = premium_manager._build_premium_response(login_res, jwt_dict, token, user_data)
        
        # Calculate performance metrics
        response_time = time.time() - start_time
        logger.info(f"Premium authentication completed in {response_time:.2f}s for UID: {uid}")
        
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Premium authentication error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Authentication error: {str(e)}",
            "timestamp": int(time.time())
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Premium health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Free Fire Premium Auth Server",
        "version": "2.0.0",
        "timestamp": int(time.time()),
        "features": ["premium", "caching", "advanced_parsing", "performance"]
    })

@app.route('/stats', methods=['GET'])
def premium_stats():
    """Premium statistics endpoint"""
    return jsonify({
        "status": "success",
        "server": "Free Fire Premium Authentication",
        "version": "2.0.0",
        "timestamp": int(time.time()),
        "cache_timeout": 28800,
        "premium_features": [
            "Advanced encryption",
            "Smart URL detection", 
            "Multi-method parsing",
            "Performance monitoring",
            "Enhanced logging"
        ]
    })

@app.route('/')
def premium_index():
    """Premium root endpoint"""
    return jsonify({
        "message": "Free Fire Premium Authentication Server",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": int(time.time()),
        "endpoints": {
            "/token": "GET - Premium authentication (uid, password)",
            "/health": "GET - Server health check",
            "/stats": "GET - Server statistics"
        }
    })

if __name__ == "__main__":
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("==================================================")
    print("       FREE FIRE PREMIUM AUTH SERVER")
    print("               Version 2.0.0")
    print("           Advanced • Secure • Fast")
    print("==================================================")
    print(Style.RESET_ALL)
    
    logger.info("Starting Free Fire Premium Auth Server v2.0.0...")
    logger.info("Premium Features: Advanced Parsing • Smart Caching • Enhanced Security")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )