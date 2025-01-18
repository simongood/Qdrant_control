import json
from dotenv import dotenv_values
import os
import numpy as np

from utils.json2txt import json_2_txt
from utils.jina_embedding import jina_embedding
from utils.qdrant_control import qdrant_manager



def file_2_Qdrant_point(placeID: str,
                        config: dict = {'jina_url':str, 'jina_headers_Authorization':str},
                        folder_path: str = './') :
    '''
    #### 將一文件
            1. 轉為 'list text'
            2. 向量化 'jina embedding'
            3. 轉為一 'Qdrant point 格式 '
    ---
    #### return :

        ```
        return models.PointStruct(
                id = str(uuid.uuid4()),  # 隨機生成
                vector= vector,     # 嵌入向量
                payload= {
                    'placeID' : placeID,
                    'model_set' : model_set,
                }  # 附加資訊
            )
        ```
    '''
    file_path = f'{folder_path}/{placeID}.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

    # 1. 轉成 list[text,]
    list_text = json_2_txt(json_data)

    # 2. 向量化
    embedding_data = jina_embedding(list_text, placeID, config['jina_url'], config['jina_headers_Authorization'])

    # 3. 製造 point
    point = qdrant_manager().make_point(  placeID, 
                                    embedding_data['embedding'],
                                    embedding_data['model_set'],
                                )
    
    return point


def search_placeIDs(folder_path: str)-> np.ndarray:
    '''
    將資料夾內的所有 placeID (檔名去除 .json)
    轉成 list 傳出
    '''

    filename_nparray = np.array(os.listdir(folder_path))
    filename_nparray = np.char.replace(filename_nparray, '.json', '')    # 去除右邊 .json 格式

    return filename_nparray



def main():
    # 加載環境變量
    config = dotenv_values("./.env")
    if len(config) == 0:
        print('please check .env path')
        return False
    
    # 初始化模型
    qdrant_obj = qdrant_manager(collection_name='view_restaurant', 
                                qdrant_url=config.get("qdrant_url"),
                                qdrant_api_key= config.get("qdrant_api_key"))
    
    # 獲取所有需要處理的 placeID file name
    folder_path = './data/view_restaurant'
    placeID_nparray = search_placeIDs(folder_path)  # 全部需處理 placeID
    processed_placeID = qdrant_obj.get_points(20000)    # 已處理完的 placeID
    unprocessed_placeids = placeID_nparray[~np.isin(placeID_nparray, processed_placeID)]    # 剩餘需要處理的 placeID 數量
    print(f"全部需處理數量 : {len(placeID_nparray)} \n已處理數量 : {len(processed_placeID)} \n剩餘需處理數量 : {len(unprocessed_placeids)}")

    # 設定每批次處理的資料量
    batch_size = 250

    # 生成 points : point list
    for i in range(0, len(unprocessed_placeids), batch_size):
        batch_placeIDs = unprocessed_placeids[i:i + batch_size]
        points = []

        print(f'正在處理第 {i//batch_size + 1} 批資料, 總共{len(unprocessed_placeids)}筆----------------')
        for placeID in batch_placeIDs:
            print(f'正在處理 : 第 {i//batch_size + 1} 批 ; 第 {len(points) +1} 筆')
            point = file_2_Qdrant_point(placeID, config, folder_path)   # 將文件轉成 point
            points.append(point)

        # 上傳 Qdrant
        if len(points) > 0:
            print(f'正在上傳第 {i//batch_size + 1} 批資料，共 {len(points)} 筆')
            qdrant_obj.qdrant_upsert_data(points)
            qdrant_obj.get_points()
    
    qdrant_obj.get_collections()
main()