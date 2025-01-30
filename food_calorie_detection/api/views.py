import time
import json
import mimetypes
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


@method_decorator([csrf_exempt,login_required], name='dispatch')
class DetectView(View):
    def post(self, request, *args, **kwargs):
        uploaded_files = request.FILES.getlist('files')
        if not uploaded_files:
            uploaded_files = request.FILES.getlist('file')
        
        if not uploaded_files:
            return JsonResponse({'error': 'No files uploaded'}, status=400)
        
        results = []

        for uploaded_file in uploaded_files:
            # 确定文件类型
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            is_image = mime_type and mime_type.startswith('image')
            is_video = mime_type and mime_type.startswith('video')

            # 保存上传的文件到临时目录
            temp_path = default_storage.save(f'temp/{uploaded_file.name}', ContentFile(uploaded_file.read()))
            temp_file_path = default_storage.path(temp_path)

            # 获取检测器实例
            detector = self.get_detector()

            try:
                # 重置检测器的检测项
                detector.detected_items = []
                detector.current_id = 1

                start_time = time.time()
                # 执行检测，传递 source 参数
                detector.detect(source=temp_file_path)

                # 构造保存路径
                save_dir = detector.save_dir / uploaded_file.name
                if not save_dir.exists():
                    save_dir = detector.save_dir / f'{uploaded_file.name}'

                # 构造可访问的 URL
                result_url = "http://127.0.0.1:8000/" + str(save_dir).replace("\\","/")
                if is_image:
                    result_image_url = result_url
                    result_video_url = None
                elif is_video:
                    result_video_url = result_url
                    result_image_url = None
                else:
                    result_image_url = result_url
                    result_video_url = None

                # 计算处理时间
                process_time = f"{float(str(time.time()-start_time)[:4])}s"
                print(f"completed!:{process_time}")

                # 收集每个文件的检测结果
                file_result = {
                    'original_file': uploaded_file.name,
                    'results': detector.detected_items,  # 包含 id, class_name, confidence, bbox
                    'completed': process_time
                }
                if is_image:
                    file_result['result_image'] = result_image_url
                if is_video:
                    file_result['result_video'] = result_video_url

                results.append(file_result)
            
            except Exception as e:
                print("***********ERROR:", e)
                results.append({'error': str(e), 'original_file': uploaded_file.name})
            finally:
                # 清理临时文件
                default_storage.delete(temp_path)

        return JsonResponse({'message': 'Detection complete!', 'results': results})
    
    def get_detector(self):
        # 获取Django应用配置
        from django.apps import apps
        api_config = apps.get_app_config('api')
        return api_config.detector


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'message': '登录成功！'})
            else:
                return JsonResponse({'error': '账号或密码错误，请重试！'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt,name='dispatch')
class CheckAuthView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({'authenticated': True, 'username': request.user.username})
        else:
            return JsonResponse({'authenticated': False}, status=401)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': '用户名和密码不能为空。'}, status=400)
            
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': '用户名已存在。'}, status=400)
            
            user = User.objects.create_user(username=username, password=password)
            user.save()
            login(request, user)
            return JsonResponse({'message': '注册成功。'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request, *args, **kwargs):
        try:
            logout(request)
            return JsonResponse({'message': 'Logout successful'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)