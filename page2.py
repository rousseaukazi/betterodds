import streamlit as st

def show():
    st.title("Page 2")

    if 'refresh_component_page2' not in st.session_state:
        st.session_state.refresh_component_page2 = False

    def toggle_refresh():
        st.session_state.refresh_component_page2 = not st.session_state.refresh_component_page2

    st.write("This is Page 2.")

    if st.button("Refresh Component on Page 2"):
        toggle_refresh()

    if st.session_state.refresh_component_page2:
        st.write("This component on Page 2 has been refreshed.")
    else:
        st.write("This component on Page 2 has not been refreshed yet.")
