import asyncio  # Import asyncio to handle async operations
from characterai import aiocai
import streamlit as st

async def inspect_methods():
    token = '67c42f8f986f526fe33a8630b9bdbbf97b219783'  # Replace with your actual token
    character_id = 'f4hEGbw8ywUrjsrye03EJxiBdooy--HiOWgU2EiRJ0s'  # Replace with your actual character ID

    try:
        client = aiocai.Client(token)
        me = await client.get_me()  # Get your client information
        async with await client.connect() as chat:  # Connect to Character.AI
            new_chat, first_message = await chat.new_chat(character_id, me.id)

            # Print the methods and attributes of the client and new_chat
            st.write(f"Methods and attributes of client object: {dir(client)}")
            st.write(f"Methods and attributes of new_chat object: {dir(new_chat)}")
    except Exception as e:
        st.write(f"An error occurred: {e}")

# Streamlit UI
st.title("Inspect Methods")
if st.button('Inspect Methods'):
    asyncio.run(inspect_methods())  # Run the inspection on button click
