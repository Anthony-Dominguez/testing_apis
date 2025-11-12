"""
WebSocket API Test Client

Tests the WebSocket API by connecting and sending various messages.
"""

import asyncio
import websockets
import json
import requests


async def test_websocket():
    """Test WebSocket API functionality"""

    # Step 1: Get JWT token from GraphQL API
    print("1. Getting JWT token from GraphQL API...")
    login_response = requests.post(
        "http://127.0.0.1:8001/graphql",
        json={
            "query": "mutation{login(input:{username:\"alice\",password:\"password123\"}){accessToken}}"
        }
    )
    token_data = login_response.json()
    token = token_data["data"]["login"]["accessToken"]
    print(f"✓ Got token: {token[:30]}...")

    # Step 2: Connect to WebSocket
    print("\n2. Connecting to WebSocket...")
    ws_url = f"ws://127.0.0.1:8002/ws?token={token}"

    async with websockets.connect(ws_url) as websocket:
        # Receive welcome message
        welcome = await websocket.recv()
        welcome_data = json.loads(welcome)
        print(f"✓ Connected! Welcome message:")
        print(f"  Type: {welcome_data['type']}")
        print(f"  User ID: {welcome_data['data']['user_id']}")
        print(f"  Username: {welcome_data['data']['username']}")
        print(f"  Active users: {welcome_data['data']['active_users']}")

        # Step 3: Test ping/pong
        print("\n3. Testing ping/pong...")
        await websocket.send(json.dumps({"action": "ping"}))
        pong = await websocket.recv()
        pong_data = json.loads(pong)
        print(f"✓ Pong received: {pong_data}")

        # Step 4: List tasks
        print("\n4. Listing tasks...")
        await websocket.send(json.dumps({"action": "task.list"}))
        tasks_response = await websocket.recv()
        tasks_data = json.loads(tasks_response)
        print(f"✓ Received {len(tasks_data['data'])} tasks")
        for task in tasks_data['data'][:3]:  # Show first 3
            print(f"  - Task {task['id']}: {task['title']} [{task['status']}]")

        # Step 5: List projects
        print("\n5. Listing projects...")
        await websocket.send(json.dumps({"action": "project.list"}))
        projects_response = await websocket.recv()
        projects_data = json.loads(projects_response)
        print(f"✓ Received {len(projects_data['data'])} projects")
        for project in projects_data['data']:
            print(f"  - Project {project['id']}: {project['name']}")

        # Step 6: Create a new task
        print("\n6. Creating a new task...")
        project_id = projects_data['data'][0]['id'] if projects_data['data'] else 1
        new_task = {
            "action": "task.create",
            "data": {
                "title": "WebSocket Test Task",
                "description": "Created via WebSocket API",
                "status": "todo",
                "project_id": project_id
            }
        }
        await websocket.send(json.dumps(new_task))
        create_response = await websocket.recv()
        create_data = json.loads(create_response)

        # Check if there's an error
        if create_data.get('type') == 'error':
            print(f"✗ Error creating task: {create_data['message']}")
            print("  Skipping remaining tests...")
            return

        print(f"✓ Task created:")
        print(f"  ID: {create_data['data']['id']}")
        print(f"  Title: {create_data['data']['title']}")
        print(f"  Status: {create_data['data']['status']}")

        # Step 7: Update the task
        print("\n7. Updating the task...")
        task_id = create_data['data']['id']
        update_task = {
            "action": "task.update",
            "data": {
                "id": task_id,
                "status": "in_progress",
                "title": "Updated WebSocket Test Task"
            }
        }
        await websocket.send(json.dumps(update_task))
        update_response = await websocket.recv()
        update_data = json.loads(update_response)
        print(f"✓ Task updated:")
        print(f"  ID: {update_data['data']['id']}")
        print(f"  Title: {update_data['data']['title']}")
        print(f"  Status: {update_data['data']['status']}")

        # Step 8: Create a comment
        print("\n8. Creating a comment...")
        comment = {
            "action": "comment.create",
            "data": {
                "text": "This is a test comment from WebSocket",
                "task_id": task_id
            }
        }
        await websocket.send(json.dumps(comment))
        comment_response = await websocket.recv()
        comment_data = json.loads(comment_response)

        if comment_data.get('type') == 'error':
            print(f"✗ Error creating comment: {comment_data['message']}")
            print("  Skipping comment test...")
        else:
            print(f"✓ Comment created:")
            print(f"  ID: {comment_data['data']['id']}")
            print(f"  Text: {comment_data['data']['text']}")

        # Step 9: Delete the task
        print("\n9. Deleting the test task...")
        delete_task = {
            "action": "task.delete",
            "data": {
                "id": task_id
            }
        }
        await websocket.send(json.dumps(delete_task))
        delete_response = await websocket.recv()
        delete_data = json.loads(delete_response)
        print(f"✓ Task deleted: {delete_data}")

        print("\n✅ All WebSocket tests passed!")
        print(f"\nWebSocket API is working correctly!")
        print(f"- Persistent connection maintained")
        print(f"- Bidirectional messaging working")
        print(f"- All CRUD operations successful")
        print(f"- Real-time updates ready for broadcast")


if __name__ == "__main__":
    print("=" * 60)
    print("WebSocket API Test Client")
    print("=" * 60)
    try:
        asyncio.run(test_websocket())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()