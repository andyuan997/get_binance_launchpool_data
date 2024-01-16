from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

def load(driver, pool_or_pad):
    while True:
        try:
            # 滾動到頁面底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)  # 等待頁面加載

            # 點擊“查看更多”按鈕
            if pool_or_pad == "pool":
                load_more_button = driver.find_element(By.CLASS_NAME, 'css-1l49ztv')
            else:
                load_more_button = driver.find_element(By.CLASS_NAME, 'css-1t0wmnf')

            load_more_button.click()
            sleep(2)  # 等待新內容加載
            print("加載中...")
        except (NoSuchElementException, ElementNotInteractableException):
            # 如果找不到按鈕或按鈕不可互動，則退出循環
            print("載入完成。")
            break

def pool_get_data(drive):
    # 提取所有項目名稱
    project_names = []
    project_elements = driver.find_elements(By.CSS_SELECTOR, 'img.css-n0oash')
    for element in project_elements:
        project_name = element.get_attribute('alt')
        if project_name:
            project_names.append(project_name)

    coin_names = project_names
    #print(coin_names)

    # 提取所有包含 class="css-153t1uw" 的 <div> 元素的文本
    data_elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-153t1uw')
    data_texts = [element.text for element in data_elements]

    details = data_texts
    #print(details)

    # 提取所有包含 class="css-1x5xp1g" 的 <div> 元素的文本
    data_elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-1x5xp1g')
    data_texts = [element.text for element in data_elements]

    input_coin_names = data_texts
    #print(input_coin_names)

    return coin_names, details, input_coin_names

def pad_get_data(drive):
    data_elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-1q7tw3q')
    data_texts = [element.text for element in data_elements]

    names = data_texts

    data_elements = driver.find_elements(By.CSS_SELECTOR, 'div.css-vurnku')
    data_texts = [element.text for element in data_elements]

    times = data_texts

    return names, times

def conform_details(details):
    data = details
    groups = []

    # 定義一個函數來檢查字符串是否為有效日期格式
    def is_valid_date(s):
        try:
            if len(s) == 10 and s[4] == '-' and s[7] == '-':
                int(s[:4])  # 年
                int(s[5:7])  # 月
                int(s[8:])  # 日
                return True
        except ValueError:
            pass
        return False

    i = 0
    while i < len(data):
        # 每組分別有[數值, 天數, 日期]，如果沒有日期則填入"無"
        group = [data[i], data[i + 1]]
        if i + 2 < len(data) and is_valid_date(data[i + 2]):
            group.append(data[i + 2])
            i += 3
        else:
            group.append("無")
            i += 2
        groups.append(group)

    return groups

def conform_input_coin_names(input_coin_names):
    data = input_coin_names

    organized_data = {}

    for item in data:
        # 分割每條資料以獲取質押的幣種和獎勵類型
        parts = item.split('，')
        if len(parts) == 2:
            pledge, reward = parts
            reward = reward.split('獲取')[1][:-2]  # 去除'獲取'和'獎勵'
            pledge = pledge.split('質押')[1]  # 去除'質押'

            # 將質押的幣種加入到對應獎勵類型的列表中
            if reward in organized_data:
                organized_data[reward].add(pledge)
            else:
                organized_data[reward] = {pledge}

    # 將集合轉換成列表以便於閱讀
    for reward in organized_data:
        organized_data[reward] = list(organized_data[reward])

    return organized_data

def pool_conform_all_data(data1, data2):

    data1 = data1
    data2 = data2

    # 創建DataFrame
    df2 = pd.DataFrame([(k, ', '.join(v)) for k, v in data2.items()], columns=['名稱', '支援幣種'])
    df1 = pd.DataFrame(data1, columns=['數量', '天數', '結束日期'])

    # 合併
    df1['Index'] = df1.index
    df2['Index'] = df2.index
    merged_df = pd.merge(df2, df1, on='Index').drop('Index', axis=1)

    return merged_df

def conform_times(times):
    dates = [item for item in times if item.count('-') == 2 and len(item) == 10]
    return dates

def pad_conform_all_data(data1, data2):

    data1 = data1
    data2 = data2

    # 創建DataFrame
    df = pd.DataFrame({
        '名稱': data1,
        '結束日期': pd.Series(data2).reindex(range(len(data1))).fillna('無')
    })

    return df

if __name__ == '__main__':
    """
    launchpool = lp
    launch pad = lpd
    """

    # 啟動WebDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    driver.get('https://launchpad.binance.com/zh-TC/viewall/lp')

    pool_or_pad = "pool"
    load(driver, pool_or_pad)
    coin_names, details, input_coin_names = pool_get_data(driver)

    # 整理後的數量、天數、結束日期
    #print(conform_details(details))

    # 整理後的使用哪幾種幣種挖礦
    #print(conform_input_coin_names(input_coin_names))

    merged_df = pool_conform_all_data(conform_details(details), conform_input_coin_names(input_coin_names))

    # 保存到Excel文件
    excel_path = './Binance_Launchpool.xlsx'
    merged_df.to_excel(excel_path, sheet_name='Launchpool', index=False)

    print("成功儲存!Binance_Launchpool.xlsx")


    driver.get('https://launchpad.binance.com/zh-TC/viewall/lpd')

    pool_or_pad = "pad"
    load(driver, pool_or_pad)
    names, times = pad_get_data(driver)
    #print(names, times)

    # 整理後的結束日期
    #print(conform_times(times))
    # print(conform_details(details))

    merged_df = pad_conform_all_data(names, conform_times(times))

    # 保存到Excel文件
    excel_path = './Binance_Launchpad.xlsx'
    merged_df.to_excel(excel_path, sheet_name='Launchpad', index=False)

    print("成功儲存!Binance_Launchpad.xlsx")

    sleep(3)
