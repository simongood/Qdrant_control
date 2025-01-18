'''
1. 放入 json 格式資料
2. 輸出 text 
'''


def json_2_txt(json_data:dict["評論":dict["內容":"", "日期":""]]) -> list[str]:
    '''
    - 檔案格式要求 :

        ``` 
        json_data = {
                        '評論1' : {
                            "內容": "好吃",
                            "日期": "1 個月前"
                        }
                        '評論2' : {}...
                    }
        ```

    - 輸出格式 :  

        ``` 
        list_text = [  
                        尚可,       # 評論 1
                        好吃,       # 評論 2
                        普普通通。,  # 評論 3
                    ]
        ```
    '''
    list_text = []

    for key in json_data : 
        '''
        內容優化 : 
            空格 => 、
            換行 => ,
        '''
        text = json_data[key]['內容'].replace(" ", "、").replace("\n", ",")
        list_text.append(text)

    return list_text



if __name__ == "__main__":
    import json

    file_path = './餐廳評論爬蟲/ChIJ______avQjQR2yhJGLY1Gto.json'
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)


    # print(json_data)
    list_text = json_2_txt(json_data)
    print(list_text)