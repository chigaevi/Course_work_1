import requests
from pprint import pprint
import copy
import time

def get_tokenVK():
    with open('token.txt', 'r') as file_obj:
        token = file_obj.read().strip()
    return token
def get_tokenYA():
    with open('tokenYA.txt', 'r') as file_obj:
        token = file_obj.read().strip()
    return token

class YaUploader_fromVK:
    def __init__(self, vk_id, token=get_tokenYA()):
        self.token = token
        self.id = vk_id

    def _get_upload_link(self, yadisk_file_path): # Функция получения временной ссылки на загрузку файла в каталог yadisk_file_path
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Authorization' : f'OAuth {self.token}'}
        params = {'path': yadisk_file_path, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        # if response.status_code == 200:
        #     print('we got link successfully')
        return response.json()

    def _create_folder(self, new_folder_name = 'photo_from_VK'):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Authorization': f'OAuth {self.token}'}
        params = {'path': new_folder_name, 'overwrite': 'true'}
        response = requests.put(url, headers=headers, params=params)
        if response.status_code == 201:
            print(f'folder "{new_folder_name}" created successfully')
        else:
            print(f'folder "{new_folder_name}" not created')
        return new_folder_name

    def _get_photos(self, num = 5): # num - количество загружаемых фото
        params = {'access_token': get_tokenVK(),
                  'v': '5.131',
                  'owner_id': self.id,
                  'extended': '1',
                  'photo_sizes': '1',
                  'album_id': 'profile',  # wall — фотографии со стены,
                                       # profile — фотографии профиля,
                                       # saved — сохраненные фотографии. Возвращается только с ключом доступа пользователя.
                  'rev': '1'}
        url = 'https://api.vk.com/method/photos.get'
        res = requests.get(url, params=params)
        res.raise_for_status()
        dic_photo = res.json()['response']['items']
        # pprint(dic_photo)
        result_list = []
        count = 0
        for photo in dic_photo:
            if count == num:
                continue
            file_name = photo['likes']['count']
            for photo_inf in result_list:
                if file_name in photo_inf.values():
                    file_name = str(file_name) + '_' + str(photo['date'])
            max_size_dic = photo['sizes'][-1] #Максимальный размер всегда в конце списка
            url_max_size_photo = max_size_dic['url']
            size = str(max_size_dic['height']) + '*' + str(max_size_dic['width']) + ' type-' + max_size_dic['type']
            result_dic = {'file_name': file_name, 'size': size, 'url': url_max_size_photo}
            result_list.append(result_dic)
            count += 1
        pprint(result_list)
        result_list_copy = copy.deepcopy(result_list)
        with open('photos_info.json', 'w') as photos_info:
            for photo_info in result_list_copy:
                del photo_info['url']
                photos_info.write(str(photo_info))
        self._create_folder()
        path_to_file = 'photo_from_VK/photos_info.json' #Загрузит в созданный с помощью функции _create_folder
        # path_to_file = 'photos_info.json' #Загрузит в корень Ядиска
        temp_upload_url = self._get_upload_link(path_to_file).get('href')
        response = requests.put(temp_upload_url, data=open('photos_info.json', 'rb'))
        if response.status_code == 201:
            print(f'file information uploaded successfully')
        else:
            print(f'file information not loaded')

        return result_list

    def upload(self):
        result_list = self._get_photos()

        for file_inf in result_list:
            # print('*'*50)
            # print(file_inf)
            photo_url = file_inf['url']
            name_file = str(file_inf['file_name']) + '.jpg'

            with open(name_file, 'wb') as photo_file:
                res = requests.get(photo_url)
                photo_file.write(res.content)

            path_to_file = 'photo_from_VK/' + name_file  # Загрузит в созданный с помощью функции _create_folder
            # path_to_file = name_file #Загрузит в корень Ядиска
            temp_upload_url = self._get_upload_link(path_to_file).get('href')
            response = requests.put(temp_upload_url, data=open(name_file,'rb'))
            # print(response.raise_for_status())
            if response.status_code == 201:
                print(f'file "{name_file}" successfully uploaded')
            else:
                print(f'file "{name_file}" unsuccessfully')

if __name__ == '__main__':
    id = '708212548'
    # id = '1'
    uploader_photo = YaUploader_fromVK(id)
    uploader_photo.upload()
    # uploader_photo.create_folder('new_folder')









