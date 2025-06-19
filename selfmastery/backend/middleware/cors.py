"""
CORS中间件配置
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_app_settings

settings = get_app_settings()


def setup_cors(app: FastAPI) -> None:
    """设置CORS中间件"""
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-API-Key",
            "Cache-Control",
            "Pragma",
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page",
            "X-Per-Page",
            "X-Request-ID",
            "X-Response-Time",
        ],
        max_age=86400,  # 24小时
    )


def get_cors_config():
    """获取CORS配置"""
    return {
        "allow_origins": settings.BACKEND_CORS_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Content-Language", 
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-API-Key",
            "Cache-Control",
            "Pragma",
        ],
        "expose_headers": [
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page",
            "X-Per-Page",
            "X-Request-ID",
            "X-Response-Time",
        ],
        "max_age": 86400,
    }


class CustomCORSMiddleware:
    """自定义CORS中间件"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.allowed_origins = settings.BACKEND_CORS_ORIGINS
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allowed_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type", 
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-API-Key",
            "Cache-Control",
            "Pragma",
        ]
        self.exposed_headers = [
            "X-Total-Count",
            "X-Page-Count", 
            "X-Current-Page",
            "X-Per-Page",
            "X-Request-ID",
            "X-Response-Time",
        ]
    
    async def __call__(self, scope, receive, send):
        """CORS中间件处理"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_headers = dict(scope["headers"])
        origin = request_headers.get(b"origin", b"").decode()
        method = scope["method"]
        
        # 检查是否是预检请求
        if method == "OPTIONS":
            await self._handle_preflight(scope, receive, send, origin)
            return
        
        # 处理实际请求
        await self._handle_request(scope, receive, send, origin)
    
    async def _handle_preflight(self, scope, receive, send, origin):
        """处理预检请求"""
        headers = []
        
        # 检查origin是否被允许
        if self._is_origin_allowed(origin):
            headers.append((b"access-control-allow-origin", origin.encode()))
            headers.append((b"access-control-allow-credentials", b"true"))
        
        # 添加允许的方法
        headers.append((
            b"access-control-allow-methods",
            ", ".join(self.allowed_methods).encode()
        ))
        
        # 添加允许的头部
        headers.append((
            b"access-control-allow-headers", 
            ", ".join(self.allowed_headers).encode()
        ))
        
        # 添加缓存时间
        headers.append((b"access-control-max-age", b"86400"))
        
        response = {
            "type": "http.response.start",
            "status": 200,
            "headers": headers,
        }
        
        await send(response)
        await send({"type": "http.response.body", "body": b""})
    
    async def _handle_request(self, scope, receive, send, origin):
        """处理实际请求"""
        # 创建响应拦截器
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                
                # 添加CORS头部
                if self._is_origin_allowed(origin):
                    headers.append((b"access-control-allow-origin", origin.encode()))
                    headers.append((b"access-control-allow-credentials", b"true"))
                
                # 添加暴露的头部
                if self.exposed_headers:
                    headers.append((
                        b"access-control-expose-headers",
                        ", ".join(self.exposed_headers).encode()
                    ))
                
                message["headers"] = headers
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """检查origin是否被允许"""
        if not origin:
            return False
        
        # 检查是否在允许列表中
        if origin in self.allowed_origins:
            return True
        
        # 检查通配符
        if "*" in self.allowed_origins:
            return True
        
        # 检查模式匹配（例如 *.example.com）
        for allowed_origin in self.allowed_origins:
            if allowed_origin.startswith("*."):
                domain = allowed_origin[2:]
                if origin.endswith(f".{domain}") or origin == domain:
                    return True
        
        return False


def add_cors_headers(response_headers: dict, origin: str = None) -> dict:
    """手动添加CORS头部"""
    cors_headers = {}
    
    if origin and origin in settings.BACKEND_CORS_ORIGINS:
        cors_headers["Access-Control-Allow-Origin"] = origin
        cors_headers["Access-Control-Allow-Credentials"] = "true"
    
    cors_headers.update({
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
        "Access-Control-Allow-Headers": ", ".join([
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-API-Key",
            "Cache-Control",
            "Pragma",
        ]),
        "Access-Control-Expose-Headers": ", ".join([
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page", 
            "X-Per-Page",
            "X-Request-ID",
            "X-Response-Time",
        ]),
        "Access-Control-Max-Age": "86400",
    })
    
    response_headers.update(cors_headers)
    return response_headers


def is_cors_preflight_request(method: str, headers: dict) -> bool:
    """检查是否是CORS预检请求"""
    return (
        method == "OPTIONS" and
        "Access-Control-Request-Method" in headers
    )


def validate_cors_origin(origin: str) -> bool:
    """验证CORS origin"""
    if not origin:
        return False
    
    allowed_origins = settings.BACKEND_CORS_ORIGINS
    
    # 直接匹配
    if origin in allowed_origins:
        return True
    
    # 通配符匹配
    if "*" in allowed_origins:
        return True
    
    # 模式匹配
    for allowed_origin in allowed_origins:
        if allowed_origin.startswith("*."):
            domain = allowed_origin[2:]
            if origin.endswith(f".{domain}") or origin == domain:
                return True
    
    return False