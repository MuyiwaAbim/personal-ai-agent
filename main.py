#This is the import for the Streamlit library for the interface without having to use HTML or CSS. It is a Python library that allows you to create web applications easily.
import streamlit as st
#This is importing a bunch of functions from the backend.database file. It's calling these functions to add or retrive things from the database.
from backend.database import (
    initialize_database, #creates the database tables if they don't exist yet
    create_conversation, #creates a new conversation record
    get_messages,  # retrieves messages from a conversation
    save_message,  #savees the user's or AI's message to the database
    save_personal_note,  # saves a personal note to the database
    get_personal_notes #retrieves all personal notes from the database
)
#This is importing the upload_document function from the backend.document_manager file. This function is responsible for handling the uploading of documents to Google's file search service.
from backend.document_manager import upload_document

#This imports the generate_response function from the backend.agent file. This function is responsible for generating a response from the AI based on the user's input and the conversation history.
from backend.agent import generate_response


# Configure application
st.set_page_config(
    page_title="Muyiwa's Personal AI",
    page_icon="🧠",
    layout="wide"
)

# This initialize database (checks if it doesn't exist and creates it if necessary)
initialize_database()


# This checks to see if the conversation id is already stored in the session. If not, it creates a new conversation and stored the ID.
if "conversation_id" not in st.session_state:

    st.session_state.conversation_id = create_conversation()


# Application title
st.title("🧠 Muyiwa's Personal AI 🧠")

#The caption
st.caption(
    "Your personal assistant, powered by Gemini."
)


# Sidebar
with st.sidebar:

    st.header("Muyiwa Knowledge Base")

    st.write("Upload documents to teach your assistant about you.")

    #Stores the uploaded files of the specified types in the list as a list variable called uploaded_files.
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt", "md", "json", "csv"],
        accept_multiple_files=True
    )
    #only enables the upload button if the uploaded_files list isn't empty.
    if st.button(
        "Upload Documents",
        disabled=not uploaded_files
    ):

        try:

            progress = st.progress(0)

            for index, uploaded_file in enumerate(uploaded_files):

                upload_document(uploaded_file)

                progress.progress(
                    (index + 1) / len(uploaded_files)
                )

            st.success("Documents uploaded successfully!")

        except Exception as error:

            st.error(f"Upload failed: {error}")


    st.divider()

    # Personal memory section
    st.header("Personal Memory")

    new_note = st.text_area(
        "Save something about yourself"
    )

    if st.button("Save Memory"):

        if new_note.strip():

            save_personal_note(new_note)

            st.success("Memory saved!")

        else:

            st.warning("Please enter something first.")


    # Display saved notes
    st.subheader("Saved Notes")

    notes = get_personal_notes()

    if notes:

        for note in notes:

            st.caption("• " + note)

    else:

        st.caption("No saved notes yet.")


    st.divider()

    # Start a new conversation
    if st.button("New Conversation"):

        st.session_state.conversation_id = create_conversation()

        st.rerun()


# Retrieve conversation history
conversation_id = st.session_state.conversation_id

messages = get_messages(conversation_id)


# Display previous messages
for message in messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# Chat input
user_input = st.chat_input(
    "Ask me anything about yourself..."
)


if user_input:

    # Save user message
    save_message(
        conversation_id,
        "user",
        user_input
    )

    # Display user message
    with st.chat_message("user"):

        st.markdown(user_input)


    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                # Retrieve previous conversation messages
                history = get_messages(conversation_id)

                # Exclude current message because it is passed separately
                response = generate_response(
                    user_input,
                    history[:-1]
                )

                st.markdown(response)

                # Save AI response
                save_message(
                    conversation_id,
                    "assistant",
                    response
                )

            except Exception as error:

                st.error(f"An error occurred: {error}")
