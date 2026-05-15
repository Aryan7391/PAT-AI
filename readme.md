1. Create Chat

POST:

http://127.0.0.1:5000/api/chats

Body:

{
  "name": "PAT_7 Test"
}

You’ll get:

{
  "chat_id": 1,
  "name": "PAT_7 Test"
}
2. Load Chat

THIS IS THE STEP YOU KEEP SKIPPING.

POST:

http://127.0.0.1:5000/api/load_chat

Body:

{
  "chat_id": 1
}

Expected response:

{
  "status": "ok",
  "chat_id": 1
}

Now:

active_chat_id = 1

inside SessionManager.

3. NOW Send Message

POST:

http://127.0.0.1:5000/api/message

Body:

{
  "message": "Explain REST APIs"
}