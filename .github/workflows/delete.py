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

    # 削除対象となる日時を計算（2日前）
    limit_date = datetime.now(timezone.utc) - timedelta(days=EXPIRE_DAYS)
    
    # 自分のユーザーIDを取得
    api_url = f"https://{SERVER}/api"
    i_url = f"{api_url}/i"
    user_res = requests.post(i_url, json={"i": TOKEN})
    if user_res.status_code != 200:
        print(f"Error: Failed to get user info. {user_res.text}")
        return
    user_id = user_res.json().get('id')

    # 自分のノートを取得して削除
    notes_url = f"{api_url}/users/notes"
    params = {
        "userId": user_id,
        "limit": 100,
        "i": TOKEN
    }

    res = requests.post(notes_url, json=params)
    if res.status_code != 200:
        print(f"Error: Failed to get notes. {res.text}")
        return

    notes = res.json()
    deleted_count = 0

    for note in notes:
        # 投稿日時を取得
        created_at = datetime.fromisoformat(note['createdAt'].replace('Z', '+00:00'))
        
        # 指定日数より古いかチェック
        if created_at < limit_date:
            delete_url = f"{api_url}/notes/delete"
            del_res = requests.post(delete_url, json={"i": TOKEN, "noteId": note['id']})
            if del_res.status_code == 204 or del_res.status_code == 200:
                print(f"Deleted: {note['id']} ({note['createdAt']})")
                deleted_count += 1
            else:
                print(f"Failed to delete: {note['id']}")

    print(f"Successfully deleted
