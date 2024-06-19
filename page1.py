import streamlit as st

def show():
    st.title("Page 1")

    if 'refresh_component' not in st.session_state:
        st.session_state.refresh_component = False

    def toggle_refresh():
        st.session_state.refresh_component = not st.session_state.refresh_component

    st.write("This is Page 1.")

    if st.button("Refresh Component on Page 1"):
        toggle_refresh()

    if st.session_state.refresh_component:
        st.write("This component on Page 1 has been refreshed.")
    else:
        st.write("This component on Page 1 has not been refreshed yet.")
