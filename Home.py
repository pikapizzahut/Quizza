import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random


cola, colb = st.columns(2, gap = "large")
with cola:
    st.title("Quizza :pizza:")

with colb:
    with st.popover("What is this?", use_container_width = True):
        st.write("Welcome to Quizza! A quiz app developed by :rainbow[Pikapizza]")
        with st.expander("What is this quiz?"):
            st.markdown("The questions of this quiz are for first year dental students")
        with st.expander("How to use?"):
            st.markdown("Use the `filter` to filter questions by topic. Go back and forth through the questions with the `Previous question` and `Next question` buttons.")
        with st.expander("Will this be updated?"):
            st.markdown("That's the plan! I'm planning to add functionality to input your own spreadsheets/database of questions to quiz from.")

st.divider()

conn = st.connection("gsheets", type=GSheetsConnection)
bank = conn.read() # Pandas df

if 'df' not in st.session_state:
    st.session_state['df'] = bank

if 'idx' not in st.session_state:
    st.session_state['indexes'] = st.session_state['df'].index
    index = random.choice(st.session_state['indexes'])
    st.session_state['idx'] = index
    st.session_state['question'] = st.session_state['df'].iloc[st.session_state['idx']]

    st.session_state['history'] = [index]
    st.session_state['correct'] = [None]
    st.session_state['answers'] = [None]
    st.session_state['pointer'] = 0
    st.session_state['no_more'] = True

#### FILTER
with st.expander("Filter"):
    with st.form("Filter", border = False):
        topics = bank['Topic'].unique()
        topic_options = st.multiselect(
        'Topics', topics, label_visibility = "collapsed", placeholder = "Choose topics")

        filter_submit = st.form_submit_button("Apply filter")
        if filter_submit:
            if len(topic_options) != 0:
                st.session_state['indexes'] = bank[bank['Topic'].isin(topic_options)].index
            else:
                st.session_state['indexes'] = bank.index

#### GET NEW Q
col1, col2, col3 = st.columns(3, gap = "large")
with col1:
    if st.button("Previous question", use_container_width = True):
        if st.session_state['pointer'] > 0:
            st.session_state['pointer'] -= 1
        else:
            st.toast("There is no previous question!")
        st.session_state['idx'] = st.session_state['history'][st.session_state['pointer']]
        st.session_state['question'] = st.session_state['df'].loc[st.session_state['idx']]

with col3:
    if st.button("Next question", use_container_width= True):
        st.session_state['pointer'] += 1
        if st.session_state['pointer'] == len(st.session_state['history']):
            st.session_state['idx'] = random.choice(st.session_state['indexes'])
            st.session_state['history'].append(st.session_state['idx'])
            st.session_state['correct'].append(None)
            st.session_state['answers'].append(None)
        else:
            st.session_state['idx'] = st.session_state['history'][st.session_state['pointer']]
        st.session_state['question'] = st.session_state['df'].loc[st.session_state['idx']]

#### QUESTION
question = st.session_state['question']

with st.form("QnA"):
    st.write(question["Question"])
    if type(question["Link"]) == str:
        st.image(question["Link"])

    options = question[[5,6,7,8,9]]
    selected = st.session_state['answers'][st.session_state['pointer']]
    answer = st.radio("Question", options, label_visibility = "collapsed", index = selected)

    answer_submit = st.form_submit_button("Submit")
    if answer_submit:
        if answer != None:
            st.session_state['answers'][st.session_state['pointer']] = options.to_list().index(answer)
            if options[int(question["Answer"])- 1] == answer:
                # st.success("You got it right!", icon="✅")
                st.session_state['correct'][st.session_state['pointer']] = True
            else:
                # st.error("Unfortunately incorrect...", icon="🚨")
                st.session_state['correct'][st.session_state['pointer']] = False
            if type(question["Notes"]) == str:
                st.write(question["Notes"])
            st.rerun()
        else:
            st.warning("You must answer with one of the options!")
    if st.session_state['correct'][st.session_state['pointer']] == True:
        st.success("You got it right!", icon="✅")
    elif st.session_state['correct'][st.session_state['pointer']] == False:
        st.error("Unfortunately incorrect...", icon="🚨")
    

with st.sidebar:
    st.metric("Developed by :rainbow[Pikapizza]","Quizza 🍕")

    st.divider()

    with st.container(border = True):
        ls_correct = [False if v is None else v for v in st.session_state['correct']]
        st.metric("**Number of questions answered**", f"{len(st.session_state['history'])}")
        st.metric("**Percent correct**", f"{round(sum(ls_correct)/len(st.session_state['history'])*100,0)}%")
    
    st.divider()

    st.markdown("**Filtered topics**")
    st.write(topic_options)
    st.markdown(f"**{len(st.session_state['indexes'])}** questions available")

    st.divider()

    st.progress((st.session_state['pointer'] + 1)/len(st.session_state['history']), text = f"Question number {st.session_state['pointer'] + 1}")
