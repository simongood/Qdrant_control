# feature/retrival
### 向量搜索資料庫端
- 使用方法步驟 :

    ```
    # 1. 初始化物件
    qdrant_obj = qdrant_search(collection_name, config, score_threshold, limit) # config 要求請看物件說明文件
        '''
        * collection_name 設定 : 看下方資料庫設定
        * config 要求 : 請看物件內容說明
        * score_threshold : 分數限制 
        * limit : 回傳數量限制
        '''

    # 2. 選擇方法
    result = qdrant_obj.cloud_search(input_query)   # for 情境搜尋
    result = qdrant_obj.trip_search(input_query)    # for 旅遊演算法

    ```
---
# 資料庫設定 
- 測試資料 collection_name 設定:
    -  collection:
        `view_restaurant_test`  ; 景點 + 餐廳資料 => 60 筆

- 正式資料 collection_name 設定:
    - collection:
        `view_restaurant` ; 景點 + 餐廳資料

> 上面兩個名稱都會鎖住不能更動

--- 

# 本地前置作業 (會動到資料庫請勿操作) : 
1. 向量化資料
2. 上傳雲端

* ### 單一文件上傳流程 `put_data2qdrant.py`
    1. text = 將文件格式化 json -> txt 以空白分割結合
    2. `jina-embeding(` text `)`  : 向量化資料
    3. 少量上傳 Qdrant 資料庫

> ps. 非批量大數上傳 ; 判別方法是每一個文件都呼叫一次 qdrant 有沒有相同的以免重複上傳 -> 所以速度較慢

> 目前設定將 main() 去除所以無法使用

> 若想要試用看看請更換 qdrant_api_key 誤動到專題資料

---

* #### env example:

```
# jina API
jina_url = '123'
jina_headers_Authorization= '123'

# qdrant url 
qdrant_url = '123'
qdrant_api_key = '123'
```

* #### 資料來源 :
> qdrant_api_key 申請 : 'https://qdrant.tech/'

> jina_headers_Authorization 申請 : 'https://jina.ai/'