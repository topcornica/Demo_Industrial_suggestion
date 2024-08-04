import time
import os
import joblib
import streamlit as st
import google.generativeai as genai
import docx 
from dotenv import load_dotenv
load_dotenv()

def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

col1, col2 = st.columns((1, 1))
with col1:
    # Selection box (Equipment)
    equipment = ["Heat Exchanger (E-101, E-102, E-103)", "Pump (P-101)", "Process Vessel (T-101, T-102)"]
    option_equip = st.selectbox(
        "Equipment?",
        (equipment[0], equipment[1], equipment[2]),
        )

with col2:
    # Selection box (Situation)
    situation = ["Situation 1", "Situation 2"]
    option_situ = st.selectbox("Troubleshooting Situation?",
        (situation[0], situation[1]))
if option_equip == equipment[0] and option_situ == situation[0]:
    scenario = "Target temperature of stream 6 (Before input to stripper) is 113 degree celcius but It's only 100 degree celcius now. This stream exchanges heat with stream 12 that has 125 degree celcius. If you are engineer what do you do if stream 6 is not target temperature ?"
elif option_equip == equipment[0] and option_situ == situation[1]:
    scenario = "The temperature of stream 2 is 25 degree celcius but the target is 40 degree celcius. The flow rate of stream 2 is not normally operate. It decrease over time. What's happen in this Heat Exchanger?"
elif option_equip == equipment[1] and option_situ == situation[0]:
    scenario = "Target pressure of stream 5 is 3 bar but it's only 2.5 bar now. If it's not fix, cavitation will happen. What does engineer do in this case?"
elif option_equip == equipment[1] and option_situ == situation[1]:
    scenario = "The pump does not have fluid input. What does engineer do in this case?"
elif option_equip == equipment[2] and option_situ == situation[0]:
    scenario = "Normal Pressure in process vessel is 3 bar but it has 3.5 bar in process vessel. What does engineer do in this case?"
elif option_equip == equipment[2] and option_situ == situation[1]:
    scenario = "Liquid level in process vessel is so high from set point. Does engineer have idea for fix this problem?"
st.text_area("Scenario:", scenario)

# Detemine system instruction
process_descrip = "The Carbon Capture process flow is illustrated in above Figure. Initially, flue gas from the steam naphtha cracker plant is introduced as Stream 1 into the absorption column (T-101). Concurrently, lean amine from the regeneration process is fed into T-101 as Stream 2. The absorption process results in treated flue gas, which is then released from the top of T-101 as Stream 3. Meanwhile, the CO2-enriched amine exits the column as Stream 4 and is directed to a pump, where it is pressurized to 2.9 bar. Subsequently, this rich amine stream enters the heat exchanger (E-101), where it encounters the hot lean amine stream (Stream 12) emerging from the stripper. Exiting E-101 at approximately 113°C as Stream 6, it then passes through a cooler, reducing its temperature to 112.85°C, before being channeled into the stripper. Within the stripper (T-102), CO2 is separated and expelled as Stream 8 after passing through a partial condenser. The process culminates with the regenerated amine exiting the base of the stripper as Stream 12. This stream, after traversing E-101, is then combined with make-up water and amine to maintain the desired composition of the lean amine solution before it is recirculated back into the absorption column.The control loops have 6 control loops. 2 loops are in absorption column (T-101), 1 loops is in heater (E-102), 2 loops are in desorption column (T-102) and 1 loop is in process vessel (V-101). For the absorption column (T-101), There are pressure sensor at the top of column when pressure is too excess can adjust by open the valve at the top of column (streamline 3) and level sensor at the bottom of the column when the level of liquid in the column is too much it can open the valve in the bottom of column (streamline 4). For the desorption column (T-102), they have loops like T-101. At the top, valve can adjust pressure in streamline 8 if pressure is excessive and at the bottom of column, valve can adjust liquid level in streamline 12. At the process vessel (V-101). It has control valve to adjust pressure  in vessel at  streamline 10. Finally, temperature sensor install at streamline 6 for control temperature in heater (E-102)."
if option_equip == equipment[0]:
    instruction = process_descrip + getText('HEX_data.docx')
elif option_equip == equipment[1]:
    instruction = process_descrip + getText('pump_data.docx')
else:
    instruction = process_descrip + getText('DistilColumn_data.docx')

# Google Gemini
GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
  system_instruction = instruction,
)

logo_url = 'logo\ TAISI.png'
st.sidebar.image(logo_url)

new_chat_id = f'{time.time()}'
MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '✨'

# Create a data/ folder if it doesn't already exist
try:
    os.mkdir('data/')
except:
    # data/ folder already exists
    pass

# Load past chats (if available)
try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}

# Sidebar allows a list of past chats
with st.sidebar:
    st.write('# Past Chats')
    if st.session_state.get('chat_id') is None:
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id] + list(past_chats.keys()),
            format_func=lambda x: past_chats.get(x, 'New Chat'),
            placeholder='_',
        )
    else:
        # This will happen the first time AI response comes in
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id, st.session_state.chat_id] + list(past_chats.keys()),
            index=1,
            format_func=lambda x: past_chats.get(x, 'New Chat' if x != st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_',
        )
    # Save new chats after a message has been sent to AI
    # TODO: Give user a chance to name chat
    st.session_state.chat_title = f'ChatSession-{st.session_state.chat_id}'

st.write('# TAISI AI')

# Chat history (allows to ask multiple questions)
try:
    st.session_state.messages = joblib.load(
        f'data/{st.session_state.chat_id}-st_messages'
    )
    st.session_state.gemini_history = joblib.load(
        f'data/{st.session_state.chat_id}-gemini_messages'
    )
    print('old cache')
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []
    print('new_cache made')
st.session_state.model = genai.GenerativeModel('gemini-pro')
st.session_state.chat = st.session_state.model.start_chat(
    history=st.session_state.gemini_history,
)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(
        name=message['role'],
        avatar=message.get('avatar'),
    ):
        st.markdown(message['content'])

# React to user input
if prompt := st.chat_input('Your message here...'):
    # Save this as a chat for later
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data/past_chats_list')
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append(
        dict(
            role='user',
            content=prompt,
        )
    )
    ## Send message to AI
    response = st.session_state.chat.send_message(
        prompt,
        stream=True,
    )
    # Display assistant response in chat message container
    with st.chat_message(
        name=MODEL_ROLE,
        avatar=AI_AVATAR_ICON,
    ):
        message_placeholder = st.empty()
        full_response = ''
        assistant_response = response
        # Streams in a chunk at a time
        for chunk in response:
            # Simulate stream of chunk
            # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
            for ch in chunk.text.split(' '):
                full_response += ch + ' '
                time.sleep(0.05)
                # Rewrites with a cursor at end
                message_placeholder.write(full_response + '▌')
        # Write full message with placeholder
        message_placeholder.write(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        dict(
            role=MODEL_ROLE,
            content=st.session_state.chat.history[-1].parts[0].text,
            avatar=AI_AVATAR_ICON,
        )
    )
    st.session_state.gemini_history = st.session_state.chat.history
    # Save to file
    joblib.dump(
        st.session_state.messages,
        f'data/{st.session_state.chat_id}-st_messages',
    )
    joblib.dump(
        st.session_state.gemini_history,
        f'data/{st.session_state.chat_id}-gemini_messages',
    )

    ##