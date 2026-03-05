import os
import requests
from datetime import datetime, timedelta, timezone

TOKEN = os.environ.get('TOKEN')
SERVER = os.environ.get('SERVER')
EXPIRE_DAYS = int(os.environ.get('EXPIRE_DAYS', 2))

def delete_old_posts():
    if not TOKEN or not SERVER:
        print("Error: TOKEN or SERVER is not set.")
        return

    limit_date = datetime.now(timezone.utc) - timedelta(days=EXPIRE_DAYS)
    api_url = f"https://{SERVER}/api"
    
    user_res = requests.post(f"{api_url}/i", json={"i": TOKEN})
    user_id = user_res.json().get('id')

    deleted_count = 0
    until_id = None

    # チェック回数を20回（最大2000件分）に増やして見落としを防ぎます
    for i in range(20):
        params = {
            "userId": user_id,
            "limit": 100,
            "i": TOKEN,
            "includeMyRenotes": True, # 自分のリノートも対象に含める
            "includeReplies": True    # 返信も対象に含める
        }
        if until_id:
            params["untilId"] = until_id

        res = requests.post(f"{api_url}/users/notes", json=params)
        notes = res.json()
        
        if not notes:
            break

        for note in notes:
            created_at = datetime.fromisoformat(note['createdAt'].replace('Z', '+00:00'))
            
            # 2日以上前なら削除
            if created_at < limit_date:
                del_res = requests.post(f"{api_url}/notes/delete", json={"i": TOKEN, "noteId": note['id']})
                if del_res.status_code in [200, 204]:
                    deleted_count += 1
            
            until_id = note['id']

    print(f"Successfully deleted {deleted_count} posts.")

if __name__ == "__main__":
    delete_old_posts()
