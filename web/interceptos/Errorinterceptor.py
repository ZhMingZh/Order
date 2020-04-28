from application import app
from common.libs.Helper import ops_render
from common.libs.LogService import LogService
from loguru import logger

# @logger.catch
@app.errorhandler(404)
def error_404(e):
    # logger.info(type(e))
    LogService.addErrorLog(str(e))
    return ops_render('error/error.html', {'status': 404, 'msg':'访问页面不存在'})
