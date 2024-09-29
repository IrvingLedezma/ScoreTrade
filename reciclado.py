"""
@st.cache_resource(show_spinner=False)
def get_tokenizer():
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")


def get_num_tokens(prompt):
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)


def generate_arctic_response_follow_up():

    follow_up_response = ""

    last_three_messages = st.session_state.messages[-3:]
    for message in last_three_messages:
        follow_up_response += "\n\n {}".format(message)
    prompt = [
        "Please generate one question based on the conversation thus far that the user might ask next. Ensure the question is short, less than 8 words, stays on the topic of EXIF and its importance and dangers, and is formatted with underscores instead of spaces, e.g., What_does_EXIF_mean? Conversation Info = {}. Please generate one question based on the conversation thus far that the user might ask next. Ensure the question is short, less than 8 words, stays on the topic of EXIF and its importance and dangers, and is formatted with underscores instead of spaces".format(
            follow_up_response
        )
    ]
    prompt.append("assistant\n")
    prompt_str = "\n".join(prompt)

    full_response = []
    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "prompt": prompt_str,
            "prompt_template": r"{prompt}",
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stop_sequences": stop_sequences,
        },
    ):
        full_response.append(str(event).strip())
    complete_response = "".join(full_response)

    return complete_response


def generate_arctic_response():

    prompt = [base_prompt] if base_prompt else []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("user\n" + dict_message["content"])
        else:
            prompt.append("assistant\n" + dict_message["content"])
    prompt.append("assistant\n")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 1000000:
        st.error("Conversation length too long. Please keep it under 1000000 tokens.")
        st.button(
            "🗑 Clear Chat History",
            on_click=clear_chat_history,
            key="clear_chat_history",
        )
        st.stop()
    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "prompt": prompt_str,
            "prompt_template": r"{prompt}",
            "temperature": temperature,
            "top_p": top_p,
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stop_sequences": stop_sequences,
        },
    ):
        yield str(event)


def display_question():
    st.session_state.follow_up = True


if prompt := st.chat_input(disabled=not replicate_api):

    st.session_state.show_animation = False

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message(
        "user",
        avatar="https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/user.gif",
    ):
        st.write(prompt)
if st.session_state.follow_up:

    st.session_state.show_animation = False

    unique_key = "chat_input_" + str(hash("Snowflake Arctic is cool"))

    complete_question = generate_arctic_response_follow_up()
    formatted_question = complete_question.replace("_", " ").strip()

    st.session_state.messages.append({"role": "user", "content": formatted_question})
    with st.chat_message(
        "user",
        avatar="https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/user.gif",
    ):
        st.write(formatted_question)
    st.session_state.follow_up = False

    with st.chat_message(
        "assistant",
        avatar="https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/assistant.gif",
    ):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}

        st.session_state.messages.append(message)

        full_response_prompt = generate_arctic_response_follow_up()
        message_prompt = {"content": full_response_prompt}
        st.button(
            str(message_prompt["content"]).replace("_", " ").strip(),
            on_click=display_question,
        )
if st.session_state.messages[-1]["role"] != "assistant":

    st.session_state.show_animation = False

    with st.chat_message(
        "assistant",
        avatar="https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/assistant.gif",
    ):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
        message = {"role": "assistant", "content": full_response}

        full_response_prompt = generate_arctic_response_follow_up()
        message_prompt = {"content": full_response_prompt}
        st.button(
            str(message_prompt["content"]).replace("_", " ").strip(),
            on_click=display_question,
        )

        st.session_state.messages.append(message)

if st.session_state.reset_trigger:

    unique_key = "chat_input_" + str(hash("Snowflake Arctic is cool"))

    complete_question = generate_arctic_response_follow_up()

    st.session_state.show_animation = False        
        """
