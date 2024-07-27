import streamlit as st
import pandas as pd

st.write("# Detail & Equipment")

st.write("")

st.write("### Process Detail")

st.write("")

st.image('pages/pnid_ccu.jpg', caption='Process Flow Diagram with Control loop of Carbon Capture unit using amine solution')
description = '''The Carbon Capture process flow is illustrated in above Figure. Initially, flue gas from the steam naphtha cracker plant is introduced as Stream 1 into the absorption column (T-101). Concurrently, lean amine from the regeneration process is fed into T-101 as Stream 2. The absorption process results in treated flue gas, which is then released from the top of T-101 as Stream 3. Meanwhile, the CO2-enriched amine exits the column as Stream 4 and is directed to a pump,where it is pressurized to 2.9 bar.
             
Subsequently, this rich amine stream enters the heat exchanger (E-101), where it encounters the hot lean amine stream (Stream 12) emerging from the stripper. Exiting E-101 at approximately 113°C as Stream 6, it then passes through a cooler, reducing its temperature to 112.85°C, before being channeled into the stripper.

Within the stripper (T-102), CO2 is separated and expelled as Stream 8 after passing through a partial condenser. The process culminates with the regenerated amine exiting the base of the stripper as Stream 12. This stream, after traversing E-101, is then combined with make-up water and amine to maintain the desired composition of the lean amine solution before it is recirculated back into the absorption column.'''
st.write(description)

st.write("")

st.write("### Streamline")
streamline = pd.read_csv("pages/streamline.csv")
st.write(streamline)

