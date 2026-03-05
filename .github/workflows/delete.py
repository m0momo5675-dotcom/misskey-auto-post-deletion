import os
import requests
from datetime import datetime, timedelta, timezone

# 設定の読み込み
TOKEN = os.environ.get('TOKEN')
SERVER = os.environ.get('SERVER')
EXPIRE_DAYS = int(os.environ.get('EXPIRE_DAYS', 2))

def delete_old_posts():
    if not TOKEN or not SERVER:
        print("Error: TOKEN or SERVER is not set.")
        return

    limit_date = datetime.now(timezone.utc) - timedelta(days=EXPIRE_DAYS)
    api_url = f"https://{SERVER}/api"
    
    # ユーザーID取得
    user_res = requests.post(f"{api_url}/i", json={"i": TOKEN})
    user_id = user_res.json().get('id')

    deleted_count = 0
    until_id = None

    # 100件ずつ最大5回繰り返し（計500件チェック）
    for _ in range(5):
        params = {
            "userId": user_id,
            "limit": 100,
            "i": TOKEN
        }
        if until_id:
            params["untilId"] = until_id

        res = requests.post(f"{api_url}/users/notes", json=params)
        notes = res.json()
        
        if not notes:
            break

        for note in notes:
            created_at = datetime.fromisoformat(note['createdAt'].replace('Z', '+00:00'))
            if created_at < limit_date:
                requests.post(f"{api_url}/notes/delete", json={"i": TOKEN, "noteId": note['id']})
                deleted_count += 1
            
            # 次の取得のために一番古いIDを記録
            until_id = note['id']

    print(f"Successfully deleted {deleted_count} posts.")

if __name__ == "__main__":
    delete_old_posts()
