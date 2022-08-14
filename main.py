import requests
from pprint import pprint
import json
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
    def __init__(self, vk_id , token = get_tokenYA()):
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

    def _get_photos(self):
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
        pprint(dic_photo)
        result_list = []
        for photo in dic_photo:
            likes = photo['likes']['count']
            id = photo['id']
            sizes = photo['sizes']
            for size in sizes:
                if size['type'] == 'z':
                    url_max_size_photo = size['url']
            result_dic = {'file_name': likes, 'id_photo': id, 'url': url_max_size_photo}
            result_list.append(result_dic)
        return result_list

    def get_and_upl_json(self):
        with open('photos_info.json', 'w') as photos_info:
            for photo_info in self._get_photos():
                del photo_info['url']
                photos_info.write(str(photo_info))
        with open('photos_info.json', 'r') as photos_info:
            path_to_file = 'photo_from_VK/photos_info.json'
            temp_upload_url = self._get_upload_link(path_to_file).get('href')
            response = requests.put(temp_upload_url, data=open('photos_info.json', 'rb'))
            if response.status_code == 201:
                print(f'file information uploaded successfully')
            else:
                print(f'file information not loaded')


    def upload(self):
        result_list = self._get_photos()
        for num in range(len(result_list)):
            photo_url = result_list[num]['url']
            name_file = str(result_list[num]['file_name']) + '.jpg'

            with open(name_file, 'wb') as photo_file:
                res = requests.get(photo_url)
                photo_file.write(res.content)

            path_to_file = 'photo_from_VK/' + name_file
            temp_upload_url = self._get_upload_link(path_to_file).get('href')
            response = requests.put(temp_upload_url, data=open(name_file,'rb'))
            # print(response.raise_for_status())
            if response.status_code == 201:
                print(f'file#{num+1} successfully uploaded')
            else:
                print(f'file#{num + 1} unsuccessfully')

if __name__ == '__main__':
    # id = '708212548'
    id = '1'
    uploader_photo = YaUploader_fromVK(id)
    uploader_photo.get_json()
    uploader_photo.upload()








