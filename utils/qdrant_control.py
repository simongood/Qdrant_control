from dotenv import dotenv_values
from qdrant_client import QdrantClient
from qdrant_client import models

class qdrant_manager:
    '''
    - #### 查詢

        ```
        get_collections()
        get_points(limit=10)
        is_same_placeID(placeID: str) -> bool
        ```
    ---
    - #### 刪除

        ```
        delete_point(points_id:list[str])
        delete_collection()
        ```
    ---
    - #### 創建
    
        ```
        create_collection(size=1024, distance=models.Distance.COSINE)
        ```
    ---
    - #### 增加

        ```python=
        make_point( placeID: str,
                    vector: list, 
                    model_set: dict['model':str, 'dimension':int, 'task': str], 
                ) -> dict
        qdrant_upsert_data( points: list[dict])
        ```
    '''
    def __init__(   self,
                    collection_name: str|None = 'control_collection', 
                    qdrant_url: str = 'your_qdrant_url', 
                    qdrant_api_key: str = 'your_qdrant_api_key')-> any:
        # 加載環境變量
        self.qdrant_client = QdrantClient(
                url=qdrant_url, 
                api_key=qdrant_api_key,
                timeout=20,
            )
        
        # 設定控制桶子
        self.collection_name = collection_name


    def get_collections(self):
        '''
        印出所有桶子名稱
        '''
        # 所有桶子狀況
        response = self.qdrant_client.get_collections()
        print("目前全部 collections : \n")
        for index, collection in enumerate(response.collections):
            print(index, collection.name)
        print("="*50)   

    def is_same_placeID(self, placeID: str) -> bool:
        '''
        尋找桶內有沒有相同的點
        '''
        result = self.qdrant_client.search(
                        collection_name=self.collection_name,
                        query_filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="placeID",
                                    match=models.MatchValue(
                                        value=placeID,
                                    ),
                                )
                            ]
                        ),
                        query_vector=[0.]*1024,
                        # limit=10,
                    )
        
        return len(result) > 0   # 若有 result 時返回 true

    def search_vector(self, vector: list =[0]*1024, score_threshold: float =0.8):
        '''
        - 使用 vector 搜尋向量相似點
        - 回傳 : 
        
            ```
            return [{
                    "Place ID 1":{"分數":"int"} ,   #相似分數
                    "Place ID 2":{"分數":"int"} , 
                    …, 
                    "Place ID n":{"分數":"int"} 
                }]
            ```
        '''
        result = self.qdrant_client.search(
                collection_name = self.collection_name,
                query_vector = vector,
                score_threshold = score_threshold,
                limit=200,
            )
        match_data = {}
        for point in result:
            placeID = point.payload['placeID']
            score = point.score
            match_data[placeID] = {"分數": score}

        return [match_data]


    def get_points(self, limit=10, payload_key=False):
        '''
        其中一個桶子內全部 point

        payload_key = 
            True : 只印payloadkeys ; 
            False : 印 PlaceID
        '''
        print(f'{self.collection_name}內 總共有\
                {self.qdrant_client.count(collection_name=self.collection_name)}\
                個點')
        print(f"內部前 {limit} 個點 : \n")
        # 滚动查询所有数据
        scroll = self.qdrant_client.scroll(collection_name=self.collection_name, with_payload=True, with_vectors=False, limit=limit)
        # print(scroll)
        
        if payload_key == True:
            print('index', 'id', 'key 值')
            for index, point in enumerate(scroll[0]):
                print(index+1, point.id, point.payload.keys())
        else :
            print('index', 'id                              ','placeID')
            for index, point in enumerate(scroll[0]):
                print(index+1, point.id ,point.payload['placeID'])
        print("="*50)   
    
    def delete_point(self, points_id:list[str]):
        '''
        刪除 points
        [id1, id2, id3,....] 
        '''
        before_point_count = self.qdrant_client.count(collection_name=self.collection_name).count
        result = self.qdrant_client.delete(
                                            collection_name=self.collection_name,
                                            points_selector=models.PointIdsList(
                                                points=points_id,
                                            ),
                                        )
        after_point_count = self.qdrant_client.count(collection_name=self.collection_name).count
        if result.status == "completed":
            print(f"已刪除完成, 目前有 {after_point_count} 個點, 總共刪除了 {before_point_count - after_point_count} 個點")
            print(result)
        else :
            print('無上傳成功')
            print(result)
        print("="*50)  

    def delete_collection(self):
        '''
        刪除桶子
        '''
        
        self.qdrant_client.delete_collection(collection_name=self.collection_name)
        print(f'刪除 {self.collection_name} 成功')
        

        


    def create_collection(self, size=1024, distance=models.Distance.COSINE):
        '''
        - 製造一個桶子
            size=1024  維度 ;
            distance=cosine : 計算方式  
        
        ---
        - 用法 :

        ```
        qdrant_manager('create_collection_name', "qdrant_url", "qdrant_api_key").create_collection()
        ```
        '''
        self.qdrant_client.create_collection(
                            collection_name=self.collection_name,
                            vectors_config=models.VectorParams(size=size, distance=distance),
                            )
        print(f"創建 {self.collection_name} 成功")
        self.get_collections()
        return 

    def make_point( self,
                    placeID: str|int,
                    vector: list, 
                    model_set: dict['model':str, 'dimension':int, 'task': str], 
                ) -> dict:
        '''
        ```
        input :
            placeID = placeID
            vector = [float * 1024]   # 1024 維浮點向量資料
            model_set = {  'model': 'jina-embeddings-v3',
                            'dimensions': 1024, 
                            "task": "text-matching"}
                    # embedding model set info
        ```
        ---
        #### 用法 : 

            ```
            point = qdrant_manager().make_point()
            ```

        ---
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
        * upsert need batch of points : list type
        '''
        import uuid
        point = models.PointStruct(
                    id = str(uuid.uuid4()),  # 隨機生成
                    vector= vector,     # 嵌入向量
                    payload= { 
                        'placeID' : placeID,
                        'model_set' : model_set,
                    }  # 附加資訊
                )
        return point
    

    def qdrant_upsert_data(self, points: list[dict]):
        '''
        #### 輸入資料 :
            * points : 要存入資料庫的點
        
        ---
        #### points : a batch of point
        * point : please use `make_point` function
        ---

        ```
        points = [  
            make_point( 
                placeID = 12312414, 
                vector = mock_1024_embedding, 
                model_set = {'model': '測試資料', 'dimensions': 1024, "task": "text-matching"},
            ),
            {
            "id": uuid,  # 唯一 ID
            "vector": [0.1, 0.2, 0.3],      # 嵌入向量 1024 維
            "payload": {
                'placeID' : placeID, 
                'model_set' : { 'model': 'jina-embeddings-v3','dimensions': 1024, "task": "text-matching"},
                }  # 附加資訊
            },
            ...,
        ]

        Returns:
            Operation Result(UpdateResult)
        ```
        '''
        before_point_count = self.qdrant_client.count(collection_name=self.collection_name).count
        # 使用 upsert 方法加入單筆資料
        result = self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points,  # 注意: points 是一個列表，即使只加入一筆資料
            wait=True,  # 等待資料被成功處理
        )
        after_point_count = self.qdrant_client.count(collection_name=self.collection_name).count
        if result.status == "completed":
            print(f"已上傳完成, 目前有 {after_point_count} 個點, 總共上傳了 {after_point_count - before_point_count} 個點")
            print(result)
        else :
            print('無上傳成功')
            print(result)
        print("="*50)  




if __name__ == "__main__":
    config = dotenv_values("./.env")
    qdrant_obj = qdrant_manager('view_restaurant_test', config.get("qdrant_url"), config.get("qdrant_api_key"))

    print("Qdrant 內目前總資料 : \n", "="*50)
    qdrant_obj.get_collections()
    qdrant_obj.get_points(payload_key=True)




    # 存入向量資料庫
    # point = qdrant_obj.make_point(12312414,             # 假 placeID
    #                               [0] * 1024,           # 1024 維的 0 向量資料
    #                               {'model': '測試資料', 'dimensions': 1024, "task": "text-matching"}, 
    #                             )
    # qdrant_obj.qdrant_upsert_data(points=[point])