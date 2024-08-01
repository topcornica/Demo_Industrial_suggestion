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
    scenario = "The temperature of stream 2 is 25 degree celcius but the target is 40 degree celcius. The flow rate of stream 2 is not normally operate. It decrease over time. What's happen in this Heat Excahnger?"
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
if option_equip == equipment[0]:
    instruction = " "
elif option_equip == equipment[1]:
    instruction = getText('pump_data.docx')
else:
    instruction = system_instruction="General reading\nTemperature Profile\nA distillation column's basic temperature distribution is warmer at the bottom and colder at the top. For a simple two-component distillation the temperature at the bottom is just lower than the boiling point of the heavier component. The temperature at the top of the column is just above the boiling point of the lighter component.\nAt the bottom of the column, we would like the heavy component to remain as a liquid and the lighter component to stay as a gas. So, we set the temperature at the bottom to match this requirement. This temperature is set by adding heat via a reboiler. Typically, the heat added to the bottom of the column is easy to control, via steam or hot oil flow rates.\nAt the top of the column, the situation is reversed. We would like the light component to remain a gas while the heavier component is condensed to a liquid and falls back down the column. The top temperature is set just above the boiling point of the lighter component. The temperature control situation is different here from the bottom of the column because we usually want the top product to be a liquid when we send it for storage. So, we condense all of the gas coming out of the top of the column to liquid. This liquid stream is split with some returning to the column and some going to storage. The top temperature is often controlled by changing the reflux rate, i.e., the flow rate of liquid sent back to the top of the column. A higher reflux rate means cooler liquid falls down the column against the rising warmer gas, and the top temperature is lower.\nOverall heat is added at the bottom of the column and heat is extracted at the top of the column. Inside the column, the temperature balance is created between the hot gas rising up the column and the cooler liquid falling down the column.\nPressure Profile\nThere is typically a pressure gradient across the column with the pressure being higher at the bottom of the column than at the top. This pressure gradient occurs as the liquid coming down the column impedes the flow of vapor up the column and imposes a pressure loss on the flow. In steady-state distillations, the pressure in the column is held constant, and the temperature is varied to control the composition of the product streams.\nDetail\nPressure\nUnder normal, usual conditions it is the vapor pressure of the liquid on the top tray that fixes the pressure at that location before the generated vapors exit to enter the overhead condenser. This is the basic parameter that fixes the column pressure. The pressure at other sites within the column depends on the ability of the vapors and liquids to distribute themselves up and down the column with minimum pressure drops. \nTherefore, the composition – or purity – of the liquid on the top tray rather defines what pressure the column is expected – or designed – to operate at. The external reflux ratio (L/D) has a bearing on fixing that composition – as the various L/V’s (internal reflux ratios) that are generated down the column have on the various trays’ compositions.\nWhat is L/D?\nIt is the external reflux ratio. It is defined as the ratio of the liquid returned to the column divided by the liquid removed as product, i.e., R = L/D.\nExternal reflux vas internal reflux\nAs the external reflux cools the top of the tower, vapors made of heavier fractions condense and liquid made of heavier faction flows down the tower it's referred to as internal reflux\nWhat is L/V internal reflux ratio?\n It is the liquid/vapor flow ratio inside the upper section of the column.\nAfter the top pressure is specified, the bottom pressure will be dictated by pressure drop along the column which depends on the relevant selected technology and the load of vapor and liquid inside the column. The corresponding bubble point of bottom pressure will specify the bottom temperature.\nThe purpose of reflux is to provide down-flowing liquid throughout the rectification section to contact with the up-flowing vapor in order to achieve stage-by-stage equilibrium heat and mass transfer and, hence, purification of the top product. When sub-cooled reflux is introduced to the top tray, it must be heated up to its bubble point before the lighter components will vaporize. \nWhere does the heat come from? \nThe only place it can come from is from condensing vapor that is approaching the top tray from below. When this vapor condenses, it adds to the total liquid flowing from tray 1 down the column. In other words, sub-cooled reflux introduces a greater volume (or mass or molar) flow of reflux than is delivered to the column by the external reflux flow controller.\nIf the degree of sub-cooling was constant, then this wouldn’t be such a big source of disturbance; however, this is usually not the case. The amount of sub-cooling will vary with the temperature of the cooling medium (ambient air, cooling water, another process stream, etc.).\nTemperature: The column gets cooler as you go up\nThere are two control points while fixing top and bottom boundary temperatures in a distillation column. At the bottom it is reboiler and at the top it is reflux. Within the column, the temperature gets set by relative volatility or more precisely by the partial pressure of HC [feed] according to Rault’s law. The volatility of components in the column is different. If P is the total pressure in the column, this is equal to the sum of P1 + P2 + P3 + ---- partial pressures at a different height. While total pressure is constant in the column, the partial pressures of HC components are different along with the height. Partial pressure = Mole fraction x Vapor pressure of pure component at a height [Rault’s law. Since the volatility of hydrocarbon becomes more as you go up, the vapor pressure becomes more, and consequently, saturation temperature gets lower. Therefore, the column gets cooler as we go up. In a steady state, the partial pressures do not change much.\nSub-cooled reflux will eventually trigger internal reflux and can substantially improve the quality of the top cut. The downside is it may destabilize the column in exceptional cases if it adds resistance to rising vapor in a given column diameter."

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

st.write('# AI Chat')

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