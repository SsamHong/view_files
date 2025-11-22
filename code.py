# 动态规则: 根据 score 计算等级和加分
score = input_score  # 从外部传入 input_score 变量
if score >= 90:
    level = "A"
    bonus = 100
elif score >= 80:
    level = "B"
    bonus = 50
else:
    level = "C"
    bonus = 0

# MP3文件下载功能 ( 函数内部导入所有依赖模块, 确保作用域内可用 ) 
def download_mp3(url, save_dir="."):
    """
    下载MP3文件到指定目录 ( 内部独立导入模块, 避免作用域问题 ) 
    :param url: 下载链接
    :param save_dir: 保存目录
    :return: (下载状态, 文件路径/错误信息)
    """
    # 关键修复: 在函数内部显式导入所有需要的模块
    import requests
    import os
    from urllib.parse import urlparse

    # 检查保存目录是否存在, 不存在则创建
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)  # 用exist_ok避免创建时的竞争条件

    # 从URL提取文件名 ( 兼容各种URL格式 ) 
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path).split("~")[0]  # 去掉URL中~后的多余参数
    # 文件名容错处理
    if not file_name or not file_name.endswith(".mp3"):
        file_name = "downloaded_audio.mp3"
    
    save_path = os.path.abspath(os.path.join(save_dir, file_name))  # 转为绝对路径, 更清晰

    # 下载配置
    timeout = 30  # 超时时间30秒
    chunk_size = 1024 * 1024  # 1MB分块下载 ( 平衡速度和内存占用 ) 

    try:
        # 发送GET请求 ( 添加User-Agent, 避免部分服务器拒绝爬虫请求 ) 
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, stream=True, timeout=timeout, headers=headers)
        response.raise_for_status()  # 抛出HTTP错误 ( 4xx/5xx ) 

        # 获取文件总大小 ( 容错处理, 避免服务器未返回该字段 ) 
        total_size = response.headers.get('content-length')
        total_size = int(total_size) if total_size and total_size.isdigit() else 0
        downloaded_size = 0

        # 写入文件 ( 二进制模式, 确保文件完整性 ) 
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # 过滤空块
                    file.write(chunk)
                    downloaded_size += len(chunk)

                    # 显示下载进度 ( 仅当能获取总大小时显示, 避免误导 ) 
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        # 只在进度整数倍10%且发生变化时显示, 避免刷屏
                        if int(progress) % 10 == 0 and int((downloaded_size - len(chunk)) / total_size * 100) != int(progress):
                            print(f"下载进度: {progress:.0f}%")

        # 验证文件完整性 ( 仅当有总大小时验证 ) 
        if total_size > 0 and downloaded_size < total_size * 0.95:  # 允许5%的误差 ( 部分服务器Content-Length不准 ) 
            if os.path.exists(save_path):
                os.remove(save_path)
            return (False, f"文件下载不完整 ( 已下载: {downloaded_size/1024/1024:.2f}MB, 应下载: {total_size/1024/1024:.2f}MB ), 已删除不完整文件")

        # 验证文件是否为有效MP3 ( 简单校验文件头 ) 
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            with open(save_path, 'rb') as f:
                header = f.read(4)  # MP3文件头通常包含ID3标签 ( 如ID3或3DI ) 
                if not header.startswith((b'ID3', b'3DI', b'FFF')):
                    os.remove(save_path)
                    return (False, "下载文件不是有效MP3格式, 已删除")

        return (True, save_path)

    except requests.exceptions.Timeout:
        return (False, f"下载超时 ( {timeout}秒 ), 请检查网络或稍后重试")
    except requests.exceptions.ConnectionError:
        return (False, "网络连接错误 ( 无法连接到服务器, 请检查网络是否正常 ) ")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') else '未知'
        return (False, f"HTTP错误: {e} ( 状态码: {status_code} ), 可能链接已过期或无效")
    except PermissionError:
        return (False, f"权限错误: 无法写入文件到 {save_dir}, 请以管理员身份运行或更换保存目录")
    except ImportError:
        return (False, "依赖库缺失, 请先运行命令安装: pip install requests")
    except Exception as e:
        # 清理不完整文件
        if os.path.exists(save_path) and os.path.getsize(save_path) < 1024:  # 小于1KB的文件视为无效
            os.remove(save_path)
        return (False, f"未知错误: {str(e)} ( 错误类型: {type(e).__name__} ) ")

# 执行下载 ( 目标MP3链接 ) 
mp3_url = "https://p26-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/d4e96871fd804b40be218f756e6adf61.mp3~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1794061423&x-signature=W0CErT7J0NMLSTYADi9Mm3AIoKU%3D&x-wf-file_name=000540.mp3"
download_success, download_msg = download_mp3(mp3_url)

# 结果整合 ( 包含分数计算和下载状态 ) 
final_result = {
    "level": level,
    "bonus": bonus,
    "original_score": score,
    "download_status": "成功" if download_success else "失败",
    "file_path": download_msg if download_success else None,
    "error_message": download_msg if not download_success else None
}
