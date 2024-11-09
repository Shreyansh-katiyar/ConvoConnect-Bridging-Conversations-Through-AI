import asyncio
from characterai import aiocai

async def test_characterai_chat():
    char_id = 'f4hEGbw8ywUrjsrye03EJxiBdooy--HiOWgU2EiRJ0s'  # Replace with your character ID
    token = '67c42f8f986f526fe33a8630b9bdbbf97b219783'  # Replace with your token

    try:
        client = aiocai.Client(token)  # Initialize the Client
        chat = await client.chat.get_chat(char_id)  # Get chat with character
        
        response = await chat.send_message("Hello, who are you?")
        if response and hasattr(response, 'text'):
            print("Response:", response.text)
        else:
            print("No valid response from Character.AI.")
        
    except Exception as e:
        print(f"Error: {e}")

# Run the test
asyncio.run(test_characterai_chat())
