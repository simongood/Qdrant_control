import requests

def jina_embedding(input_data: list[str], placeID: str,jina_url:str, jina_headers_Authorization:str) ->dict:
    '''
    - 輸入變數 : 

        ```
        jina_embedding(
            input_data : ['待向量資料']  # list_text
            placeID : '地點ID'
            jina_url : 'API key'
            jina_headers_Authorization : 'header'
        )
        ```

    - 輸出變數 : 

        ```
        embedding_data = {
                'placeID': '123',
                'model_set' : { 
                                'model': 'jina-embeddings-v3',
                                'dimensions': 1024, 
                                "task": "text-matching" 
                                },
                'list_text': ['我想吃牛肉麵', '我想吃飯'], 
                'embedding': [ 1024 維浮點數 ],
            }
        ```
    '''

    # jina 呼叫 API URL 、 Headers 、 請求數據 設定
    url = jina_url
    headers = {
        'Content-Type': 'application/json',
        'Authorization': jina_headers_Authorization
    }
    data = {
        "model": "jina-embeddings-v3",
        "task": "text-matching",
        "late_chunking": False,
        "dimensions": 1024,
        "embedding_type": "float",
        "input": input_data
    }


    # 發送請求
    response = requests.post(url, headers=headers, json=data)

    # 回應成功 => 萃取資料
    if response.status_code == 200:
        data = response.json()
        embedding_data = {
            'placeID': placeID,
            'model_set' : {'model': 'jina-embeddings-v3', 'dimensions': 1024, "task": "text-matching"},
            'list_text': input_data,                    # 被向量評論內容
            'embedding': data['data'][0]['embedding']   # 向量資料 : 1024 維
        }
        return embedding_data
    else:
        print(f"請求失敗, HTTP 狀態碼: {response.status_code}")
        print(response.text)


if __name__ == "__main__" :
    from dotenv import dotenv_values

    # 加載環境變量
    config = dotenv_values("./.env")
    jina_url = config.get("jina_url")
    jina_headers_Authorization = config.get("jina_headers_Authorization")
    if jina_url == None : print("檢查環境變數")


    # 執行 input data 向量化
    input_data = ["我想吃牛肉麵", "我想吃飯"]
    placeID = '123'
    embedding_data = jina_embedding(input_data, placeID, jina_url, jina_headers_Authorization)
    print(embedding_data)
