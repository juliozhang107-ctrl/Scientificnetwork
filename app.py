import random
import os
import tempfile
from pyvis.network import Network
from pyalex import Authors, Works, config

config.email = "jmz2158@cumc.columbia.edu"

COLOR_PALETTE = [
    "#FF5733", "#33A1FF", "#28B463", "#F1C40F", "#9B59B6", 
    "#E74C3C", "#1ABC9C", "#34495E", "#D35400", "#7D6608", 
    "#1F618D", "#148F77", "#B03A2E", "#7FB3D5", "#C39BD3"
]
HUB_COLORS = ["#00ffcc", "#ff00cc", "#ffff00", "#0099ff", "#ff6600", "#ccff00"]

def generate_hex_color():
    return "#" + "".join([random.choice("0123456789ABCDEF") for _ in range(6)])

def fetch_author_data(author_name):
    results = Authors().search(author_name).get()
    if not results:
        return None
    author = results[0]
    inst = author.get('last_known_institution', {}).get('display_name', "Unknown Institution")
    return {"id": author['id'], "name": author['display_name'], "inst": inst}

def generate_clustered_map(hub_names):
    """Generates the PyVis map securely inside the system's temporary directory."""
    hubs = []
    for i, name in enumerate(hub_names):
        data = fetch_author_data(name)
        if data:
            data['color'] = HUB_COLORS[i % len(HUB_COLORS)]
            hubs.append(data)

    if not hubs:
        raise ValueError("None of the requested authors could be found on OpenAlex.")

    hub_names_set = {h['name'] for h in hubs}
    coauthor_counts = {}
    institution_map = {}

    for hub in hubs:
        works = Works().filter(author={"id": hub['id']}).get()
        for work in works:
            for a in work.get('authorships', []):
                co_name = a['author']['display_name']
                if a['author']['id'] == hub['id']: continue
                
                if co_name not in coauthor_counts:
                    coauthor_counts[co_name] = {}
                coauthor_counts[co_name][hub['name']] = coauthor_counts[co_name].get(hub['name'], 0) + 1
                
                if co_name not in institution_map:
                    inst_list = a.get('institutions', [])
                    institution_map[co_name] = inst_list[0]['display_name'] if inst_list else "No Affiliation Listed"

    for h_name in hub_names_set:
        coauthor_counts.pop(h_name, None)

    unique_institutions = list(set(institution_map.values()))
    inst_color_dict = {}
    for i, inst in enumerate(unique_institutions):
        inst_color_dict[inst] = COLOR_PALETTE[i] if i < len(COLOR_PALETTE) else generate_hex_color()

    net = Network(height='750px', width='100%', bgcolor='#111111', font_color='white', cdn_resources='remote')
    
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -40,
          "centralGravity": 0.01,
          "springLength": 70,
          "springConstant": 0.06,
          "damping": 0.4,
          "avoidOverlap": 0.25
        },
        "maxVelocity": 40,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {"iterations": 150}
      }
    }
    """)

    for i, hub in enumerate(hubs):
        net.add_node(hub['name'], label=hub['name'], color=hub['color'], size=45, shape="star", title=f"Author {i+1}: {hub['name']}")

    for i in range(len(hubs)):
        for j in range(i + 1, len(hubs)):
            hub_a, hub_b = hubs[i], hubs[j]
            works_a = Works().filter(author={"id": hub_a['id']}).get()
            shared_count = sum(1 for w in works_a if hub_b['id'] in [a['author']['id'] for a in w.get('authorships', [])])
            if shared_count > 0:
                net.add_edge(hub_a['name'], hub_b['name'], color="#ffffff", value=shared_count)

    for inst in unique_institutions:
        net.add_node(f"INST_{inst}", label="", hidden=True, size=1, shape="dot")

    for coauthor, counts_per_hub in coauthor_counts.items():
        total_count = sum(counts_per_hub.values())
        inst = institution_map[coauthor]
        node_color = inst_color_dict[inst]
        
        node_size = 12 + (total_count * 4)
        is_shared = len(counts_per_hub) > 1 
        border_width = 3 if is_shared else 1
        border_color = "#ffffff" if is_shared else node_color

        connections_text = "\n".join([f"  • with {h}: {c} papers" for h, c in counts_per_hub.items()])
        title_text = f"Co-author: {coauthor}\nInstitution: {inst}\nShared Connections:\n{connections_text}"

        net.add_node(coauthor, label=coauthor, color={"background": node_color, "border": border_color},
                     borderWidth=border_width, size=node_size, shape="dot", title=title_text)
        
        for hub_name, count in counts_per_hub.items():
            h_color = next(h['color'] for h in hubs if h['name'] == hub_name)
            rgb = tuple(int(h_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            net.add_edge(hub_name, coauthor, color=f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.35)", value=count)

        net.add_edge(coauthor, f"INST_{inst}", color="rgba(0,0,0,0)", length=20)

    html_hubs_legend = "".join([f'<div style="color: {h["color"]}; font-weight: bold; margin-bottom: 4px;">★ Author: {h["name"]}</div>' for h in hubs])
    html_color_legend = "".join([f'<div style="margin-bottom: 5px; display: flex; align-items: center;"><span style="display: inline-block; width: 12px; height: 12px; background-color: {color}; margin-right: 8px; flex-shrink: 0;"></span>{inst}</div>' for inst, color in inst_color_dict.items()])
    
    legend_panel = f"""
    <div style="position: absolute; top: 20px; left: 20px; z-index: 1000; background-color: rgba(20, 20, 20, 0.9); padding: 15px; border-radius: 8px; border: 1px solid #444; max-width: 300px; max-height: 600px; overflow-y: auto; font-family: sans-serif; font-size: 11px; color: #ffffff;">
        <h4 style="margin-top: 0; color: #fff; border-bottom: 1px solid #444; padding-bottom: 5px;">Network Legend</h4>
        <div style="margin-bottom: 10px;">{html_hubs_legend}</div>
        <div style="margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 10px;">
            <strong>Node Highlights:</strong><br>● White Border = Shared Collaborator<br>● Color Group = Shared Institution
        </div>
        <strong>Institutions:</strong>{html_color_legend}
    </div>
    """

    # Ensure secure write access by utilizing the OS temporary folder structure
    temp_dir = tempfile.gettempdir()
    secure_output_path = os.path.join(temp_dir, "secure_network_map.html")
    
    net.save_graph(secure_output_path)
    
    with open(secure_output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace('<body>', f'<body>\n{legend_panel}')
    with open(secure_output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return secure_output_path
