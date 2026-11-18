"""Middlewares del proyecto ForestIA."""


class NoCacheHTMLMiddleware:
    """Las respuestas HTML (paginas dinamicas) se sirven siempre frescas.

    Sin esto, navegadores y Cloudflare aplican caching heuristico sobre
    paginas HTML que no declaran encabezados de cache, y sirven versiones
    viejas (el bug del admin sin estilos y del calendario vacio).
    Los estaticos (CSS/JS/imagenes) no se tocan: siguen cacheandose.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.headers.get("Content-Type", "")
        cache_control = response.headers.get("Cache-Control", "")
        if content_type.startswith("text/html") and "no-store" not in cache_control:
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
        return response
