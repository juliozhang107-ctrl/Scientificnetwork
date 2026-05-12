import streamlit as st
import streamlit.components.v1 as components
import os

# Import the standardized function name to prevent ImportError crashes
from network_builder import build_network_map

st.set_page_config(page_title="Research Network Mapper", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🌐 Dynamic Research Network Mapper")
st.markdown("Map intersectional collaboration networks using data fetched directly from **OpenAlex**.")

if 'author_count' not in st.session_state:
    st.session_state.author_count = 1

with st.sidebar:
    st.header("👥 Define Primary Authors")
    st.caption("Add researchers to map their shared collaborative networks.")
    
    author_inputs = []
    for i in range(st.session_state.author_count):
        val = st.text_input(f"Author {i+1}:", placeholder=f"Enter Author {i+1} Name", key=f"input_{i}")
        author_inputs.append(val)
        
    if st.button("➕ Add Author", use_container_width=True):
        st.session_state.author_count += 1
        st.rerun()
        
    if st.session_state.author_count > 1:
        if st.button("➖ Remove Last", use_container_width=True):
            st.session_state.author_count -= 1
            st.rerun()

    st.divider()
    map_triggered = st.button("🚀 Map Network", type="primary", use_container_width=True)

if map_triggered:
    valid_authors = [name.strip() for name in author_inputs if name.strip()]
    
    if not valid_authors:
        st.sidebar.error("⚠️ Please enter at least one valid author name.")
    else:
        with st.spinner("🔍 Querying OpenAlex & building visualization..."):
            try:
                # Execute the matched backend function securely
                secure_file_path = build_network_map(valid_authors)
                
                if secure_file_path and os.path.exists(secure_file_path):
                    with open(secure_file_path, 'r', encoding='utf-8') as f:
                        html_data = f.read()
                        
                    st.success("✨ Network map generated successfully!")
                    components.html(html_data, height=760, scrolling=False)
                    
                    with open(secure_file_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download standalone HTML map",
                            data=f,
                            file_name="research_network.html",
                            mime="text/html",
                            type="secondary"
                        )
                else:
                    st.error("❌ Failed to read generated map file from secure storage.")
                    
            except Exception as e:
                st.error(f"⚠️ An error occurred during graph compilation: {str(e)}")
else:
    st.info("👈 Add your primary authors in the sidebar and click **Map Network** to begin exploration.")
