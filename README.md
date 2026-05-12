# 🌐 Dynamic Research Network Mapper

A streamlined, web-based visualization tool designed to map intersectional academic collaboration networks using real-time data fetched directly from the **OpenAlex** database. 

Built with **Streamlit** and **PyVis**, this application allows researchers, clinicians, and academic institutions to explore complex co-authorship structures and hidden institutional clusters without requiring any local software installation or coding knowledge.

---

## ✨ Key Features

* **Dynamic Multi-Author Inputs:** Seamlessly add or remove multiple primary target researchers to explore how disparate academic networks cross-collaborate.
* **Live API Integration:** Queries the comprehensive OpenAlex database on-demand to fetch verified publication records, author identities, and recent institutional affiliations.
* **Invisible Institutional Clustering:** Utilizes custom `ForceAtlas2` physics to spatially group co-authors by shared institutional anchors, providing an intuitively organized layout while keeping the visual canvas free of UI clutter.
* **Interactive Exploration:** Hover over individual nodes to instantly view detailed collaboration metrics, shared paper counts broken down by primary author hubs, and distinct institutional associations.
* **Standalone HTML Exports:** Generate and download fully portable, self-contained interactive network maps directly from the browser for offline presentation or embedding.

---

## 🚀 How to Use the Interface

The tool is hosted live via **Streamlit Community Cloud** for zero-configuration public access.

1. **Access the App:** Open the live application URL in any web browser.
2. **Define Hubs:** In the left sidebar, enter the names of the primary authors you wish to map. Use the **➕ Add Author** button to dynamically introduce additional input rows.
3. **Generate Layout:** Click **🚀 Map Network**. The backend engine will silently extract co-authorship matrices and render the physics-based graph directly within the main viewing workspace.
4. **Interact & Export:** Drag nodes to explore connections, zoom in on dense collaboration clusters, or download the final interactive rendering via the native export button.

---

## 🛠️ System Architecture

* **Frontend:** Pure Python UI mapping utilizing `streamlit` and custom layout injection components.
* **Backend Engine:** `network_builder.py` bridges standard data processing pipelines (`pandas`) with live query execution via `pyalex`.
* **Physics & Graphing:** Dynamic layout vectors calculated natively via `pyvis` utilizing system-level temporary storage arrays to ensure safe execution across restricted cloud server environments.
