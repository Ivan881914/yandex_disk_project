import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
import zipfile
import tempfile
import tempfile
from urllib.parse import urlparse, parse_qs
import mimetypes
from django.core.cache import cache

YANDEX_DISK_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

def index(request):
    files = []
    error_message = None

    if request.method == 'POST' and 'public_key' in request.POST:
        public_key = request.POST.get('public_key')  # Получаем публичную ссылку

        # Ключи кэша для данных
        cache_key_data = f"yandex_disk_data_{public_key}"

        # Проверяем, есть ли данные в кэше
        cached_data = cache.get(cache_key_data)

        # Отправляем запрос к API Яндекс.Диска
        response = requests.get(YANDEX_DISK_API_URL, params={'public_key': public_key})
        
        if response.status_code == 200:
            data = response.json()

            #print("Ответ от API Яндекс.Диска: ", data)

            # Проверка на количество файлов
            if cached_data:
                cached_files_count = len(cached_data['_embedded']['items']) if '_embedded' in cached_data else 0
                current_files_count = len(data['_embedded']['items']) if '_embedded' in data else 0

                if cached_files_count == current_files_count:
                    print("--------------------------------------------  Количество файлов не изменилось, используем кэшированные данные")
                    data = cached_data
                else:
                    print("--------------------------------------------  Количество файлов изменилось, обновляем кэш")
                    cache.set(cache_key_data, data, 60 * 15)  # Кэшируем данные на 15 минут
            else:
                # Если данных в кэше нет, кэшируем данные после запроса
                cache.set(cache_key_data, data, 60 * 15) 

            if '_embedded' in data:
                items = data['_embedded']['items']
                for item in items:
                    # Получаем md5 для каждого файла
                    file_md5 = item.get('md5')
                    print(f"MD5 хеш для файла {item['name']}: {file_md5}")

                    if file_md5:
                        # Создаем уникальный ключ для каждого файла на основе его имени
                        cache_key_md5 = f"yandex_disk_file_md5_{item['name']}"
                        
                        # Проверяем, есть ли md5 в кэше
                        cached_md5 = cache.get(cache_key_md5)

                        if cached_md5 and cached_md5 == file_md5:
                            print(f"Файл {item['name']} не изменился, используем кэш")
                        else:
                            cache.set(cache_key_md5, file_md5, 60 * 15)
                            print(f"Файл {item['name']} изменился, обновляем кэш")

                
                    file_name = item['name']
                    file_mime_type, _ = mimetypes.guess_type(file_name)
                    file_size = item.get('size', 0)

                    files.append({
                        'name': item['name'],
                        'download_link': item['file'] if 'file' in item else None,
                        'mime_type': file_mime_type,
                        'size': file_size
                    })
            else:
                error_message = "По этой ссылке нет доступных файлов."
        else:
            error_message = "Ошибка при запросе к Яндекс.Диску. Проверьте правильность ссылки."

    return render(request, 'index.html', {'files': files, 'error_message': error_message})


def download_files(request):
    if request.method == 'POST':
        selected_files = request.POST.getlist('selected_files')  # Получаем список выбранных файлов

        if not selected_files:
             return HttpResponse("Вы не выбрали ни одного файла для загрузки.")

        # Создаем временный файл для архива
        temp_file = tempfile.TemporaryFile()

        # Открываем временный файл как ZIP-архив
        with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_url in selected_files:
                # Загружаем содержимое каждого файла
                response = requests.get(file_url)
                if response.status_code == 200:
                    # Извлекаем имя файла из URL
                    parsed_url = urlparse(file_url)
                    query_params = parse_qs(parsed_url.query)
                    file_name = query_params.get('filename', ['unknown'])[0]  # Используем имя файла из параметров URL
                    # Добавляем файл в архив
                    zip_file.writestr(file_name, response.content)
                else:
                    return HttpResponse(f"Не удалось загрузить файл: {file_url}")

        # После завершения записи всех файлов перемещаем указатель на начало файла
        temp_file.seek(0)

        # Создаем HTTP-ответ с файлом для скачивания
        response = HttpResponse(temp_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="files.zip"'

        return response

    return redirect('index')
