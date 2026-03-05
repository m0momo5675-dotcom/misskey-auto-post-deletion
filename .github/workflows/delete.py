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
    
    try:
        user_res = requests.post(f"{api_url}/i", json={"i": TOKEN})
        user_id = user_res.json().get('id')
    except Exception as e:
        print(f"Error connecting to server: {e}")
        return

    deleted_count = 0
    until_id = None

    for i in range(20):
        params = {
            "userId": user_id,
            "limit": 100,
            "i": TOKEN,
            "includeMyRenotes": True,
            "includeReplies": True
        }
        if until_id:
            params["untilId"] = until_id

        try:
            res = requests.post(f"{api_url}/users/notes", json=params)
            # サーバーから正しくJSONが返ってきたかチェック
            if res.status_code != 200:
                print(f"Server returned status code {res.status_code}")
                break
            notes = res.json()
        except Exception:
            print("Failed to parse notes. Ending this run safely.")
            break
        
        if not notes:
            break

        for note in notes:
            created_at = datetime.fromisoformat(note['createdAt'].replace('Z', '+00:00'))
            if created_at < limit_date:
                requests.post(f"{api_url}/notes/delete", json={"i": TOKEN, "noteId": note['id']})
                deleted_count += 1
            until_id = note['id']

    print(f"Successfully deleted {deleted_count} posts.")

if __name__ == "__main__":
    delete_old_posts()
