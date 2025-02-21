import json
from rangersdk.dsl import DSL, int_expr, string_expr, empty_expr, show
from rangersdk.client import RangersClient
import os
import pandas as pd
# AK：58dfa04aaf37f137
# SK：DBGptmzsPZviJHy9I2xERu10CUArgQ4c
ak = '58dfa04aaf37f137'
sk = 'DBGptmzsPZviJHy9I2xERu10CUArgQ4c'
url = 'https://rangers.bistream.net'
bc = RangersClient(ak, sk, url=url)

def get_user_list_list(user_ids, output_folder=None):

    # 遍历 user_list 中的每个用户
    for user in user_ids:
        user_uuid = user['user_unique_id']
        body = {
            "query_id": user_uuid,
            "query_type": "user_unique_id"
        }
        try:
            res = bc.data_finder('/openapi/v1/10000020/behaviors/profiles', body=body)
            # 解析响应内容
            user_data = json.loads(res.content)

            # 定义输出文件路径
            output_file_path = os.path.join(output_folder, f'{user_uuid}.json')

            # 将用户数据保存到文件中
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                json.dump(user_data, output_file, ensure_ascii=False, indent=4)

            print(f"用户 {user_uuid} 的数据已保存到 {output_file_path}")
        except Exception as e:
            print(f"拉取用户 {user_uuid} 的数据时出错: {e}")

    print("所有用户的行为数据已保存到指定文件夹中。")

def get_user_behavior_list(user_ids, output_folder=None):

    for user_uuid in user_ids:

        body={
            "query_id": user_uuid,
            "query_type": "user_unique_id",
            "count": 1000,
            "orientation": "earlier",
            "timestamp": 1739859278000,
        }

        try:

            res = bc.data_finder('/openapi/v1/10000020/behaviors/flows', body=body)
            # 检查响应状态码
            if res.status_code == 200:
                # 解析响应内容
                user_data = json.loads(res.content)

                # 定义输出文件路径
                output_file_path = os.path.join(output_folder, f'{user_uuid}.json')

                # 将用户数据保存到文件中
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    json.dump(user_data, output_file, ensure_ascii=False, indent=4)

                print(f"用户 {user_uuid} 的数据已保存到 {output_file_path}")
            else:
                print(f"拉取用户 {user_uuid} 的数据时出错，状态码: {res.status_code}，响应内容: {res.content}")
        except Exception as e:
            print(f"拉取用户 {user_uuid} 的行为数据时出错: {e}")

    print("所有用户的行为数据已保存到指定文件夹中。")

def get_users_after_break(user_ids, break_file_name):
    # Convert user_ids to list if needed
    user_list = user_ids.tolist() if hasattr(user_ids, 'tolist') else list(user_ids)
    
    try:
        # Find break point index
        break_index = user_list.index(break_file_name)
        # Get users after break point
        filtered_users = user_list[break_index+1:]
        return filtered_users
    except ValueError:
        print(f"Break point {break_file_name} not found in user list")
        return []


if __name__ == "__main__":
    file = r'C:\Users\jingyuan.hao\Downloads\downloaded_data.csv'
    df = pd.read_csv(file)
    user_ids = df['user_id']
    break_file_name = 'hidfile_tt__000Rjl83iWIM3bBk-egEOhhERafhpLxVGAA'
    filtered_users = get_users_after_break(user_ids, break_file_name)
    user_info_output_folder = r'C:\project\datafinder-sdk-openapi-py\quickgames_user_info'
    user_behavior_output_folder = r'C:\Users\jingyuan.hao\Downloads\user216behavior'
    # 如果文件夹不存在，则创建它
    if not os.path.exists(user_behavior_output_folder):
        os.makedirs(user_behavior_output_folder)

    # get_user_list_list()
    get_user_behavior_list(user_ids=filtered_users, output_folder=user_behavior_output_folder)