import streamlit as st
import streamlit.components.v1 as components
import os
from network_builder import build_network_map

st.set_page_config(page_title="Research Network Mapper", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🌐 Dynamic Research Network Mapper")
st.markdown("Map intersectional collaboration networks using data fetched directly from **OpenAlex**.")

# 1. State Tracking Initialization
# Instead of tracking simple raw text rows, we maintain a persistent runtime target array
if 'active_hubs' not in st.session_state:
    st.session_state.active_hubs = ["Julio Min Fei Zhang"] # Boot defaults cleanly

# Maintain session buffer to capture discovered co-authors dynamically
if 'discovered_coauthors' not in st.session_state:
    st.session_state.discovered_coauthors = []

with st.sidebar:
    st.header("👥 Active Hub Target Stack")
    st.caption("Primary researchers driving the mapping visualization.")
    
    # Render interactive input boxes reflecting the live state tracking list
    updated_hubs = []
    for i, current_name in enumerate(st.session_state.active_hubs):
        val = st.text_input(f"Hub Star {i+1}:", value=current_name, key=f"hub_{i}")
        updated_hubs.append(val)
    
    # Sync runtime modifications cleanly back into persistent core state tracking variables
    st.session_state.active_hubs = updated_hubs
        
    if st.button("➕ Manual Base Author Add", use_container_width=True):
        st.session_state.active_hubs.append("")
        st.rerun()
        
    if len(st.session_state.active_hubs) > 1:
        if st.button("➖ Drop Active Baseline Row", use_container_width=True):
            st.session_state.active_hubs.pop()
            st.rerun()

    st.divider()
    map_triggered = st.button("🚀 Render Visual Matrix", type="primary", use_container_width=True)

# Process execution loop logic
if map_triggered or st.session_state.discovered_coauthors:
    valid_authors = [name.strip() for name in st.session_state.active_hubs if name.strip()]
    
    if not valid_authors:
        st.sidebar.error("⚠️ Please maintain at least one baseline root mapping query target.")
    else:
        with st.spinner("🔍 Querying OpenAlex & building recursive visualization logic..."):
            try:
                # Capture generated mapping files alongside full parsed coauthor tracking output listings
                secure_file_path, coauthors_list = build_network_map(valid_authors)
                
                # Update global state buffer array variables cleanly
                st.session_state.discovered_coauthors = sorted(coauthors_list)
                
                if secure_file_path and os.path.exists(secure_file_path):
                    with open(secure_file_path, 'r', encoding='utf-8') as f:
                        html_data = f.read()
                        
                    st.success("✨ Interactive network structure mapped cleanly!")
                    
                    # Present visualization interface inside primary canvas space
                    components.html(html_data, height=760, scrolling=False)
                    
                    # --- INTERACTIVE EXPANSION COMPONENT CONTROLLER ---
                    st.divider()
                    st.subheader("🔗 Expand Co-Author Network")
                    st.markdown("Select any co-author discovered in the current map to promote them to a primary **Hub Star** and recursively expand their shared networks.")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        selected_expansion = st.selectbox(
                            "Select co-author target node to promote:", 
                            options=st.session_state.discovered_coauthors,
                            index=None,
                            placeholder="Choose an author to expand..."
                        )
                    with col2:
                        # Align vertical formatting cleanly directly adjacent to dynamic dropdown menu
                        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("⚡ Expand Network", type="secondary", use_container_width=True):
                            if selected_expansion and selected_expansion not in st.session_state.active_hubs:
                                # Promote selected node cleanly into active state storage list
                                st.session_state.active_hubs.append(selected_expansion)
                                st.rerun() # Refresh app runtime execution matrix instantly
                            elif selected_expansion in st.session_state.active_hubs:
                                st.warning("⚠️ Target is already active as a main Hub Star.")
                            else:
                                st.info("ℹ️ Please select a targeted target string before triggering execution logic.")
                    
                    # Standalone static rendering client export pipeline
                    with open(secure_file_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download standalone HTML map",
                            data=f,
                            file_name="recursive_research_network.html",
                            mime="text/html"
                        )
                else:
                    st.error("❌ Failed to parse memory caching layouts safely.")
                    
            except Exception as e:
                st.error(f"⚠️ An execution error halted structural processing: {str(e)}")
else:
    st.info("👈 Establish primary targets inside the left control block to trigger real-time compilation mapping.")
