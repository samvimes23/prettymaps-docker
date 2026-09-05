import streamlit as st
import logging
from matplotlib import pyplot as plt
import sys
import os
import io


def download_svg():
    """
    Creates additional map in SVG format
    """
    fig_path = "/tmp/generated_map_download.svg"
    plt.savefig(fig_path, format="svg", bbox_inches="tight", pad_inches=0.15, dpi=150)
    return fig_path


# Set Streamlit to use the wide layout
st.set_page_config(layout="wide")

# Add repo root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import prettymaps

# Initialize session state for last_image
if "last_image" not in st.session_state:
    st.session_state.last_image = None

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

presets = prettymaps.presets().to_dict()

# Set the title of the app
st.title("prettymaps")

cols = st.columns([1, 2])
with cols[0]:
    query = st.text_area(
        "Location", value="Stad van de Zon, Heerhugowaard, Netherlands", height=86
    )
    radius = st.slider("Radius (km)", 0.5, 1.5, 0.75, step=0.25)
    circular = st.checkbox("Circular map", value=False)
    poster_mode = st.checkbox("Minimalist Poster Mode", value=False)

    # Preset selector
    preset_options = list(presets["preset"].values())
    selected_preset = st.selectbox(
        "Select a Preset", preset_options, index=preset_options.index("default")
    )

    # Add input for number of colors
    style = prettymaps.preset(selected_preset).params["style"]
    palette = (
        style["building"]["palette"]
        if "building" in style and "palette" in style["building"]
        else ["#433633", "#FF5E5B"]
    )
    num_colors = st.number_input(
        "Number of colors", min_value=1, value=len(palette), step=1
    )

    custom_palette = {}
    color_cols = st.columns(len(palette))
    for i in range(len(palette) // 1):  # Calculate the number of rows needed
        for j, col in enumerate(color_cols):
            idx = i * 4 + j
            if idx < num_colors:
                color = col.color_picker(
                    f"Color {idx + 1:02d}", palette[idx % len(palette)]
                )
                custom_palette[idx] = color

    # Add page size options
    page_size_col, dpi_col = st.columns(2)
    with page_size_col:
        page_size = st.selectbox(
            "Page Size",
            ["A4", "A5", "Square"],
            index=0,
            # , "A3", "A2", "A1", "Custom"], index=0
        )
    with dpi_col:
        dpi = st.number_input("DPI", min_value=50, max_value=300, value=100, step=50)

    if page_size == "Custom":
        width = st.number_input("Custom Width (inches)", min_value=1.0, value=8.27)
        height = st.number_input("Custom Height (inches)", min_value=1.0, value=11.69)
    else:
        page_sizes = {
            "A4": (8.27, 11.69),
            "A5": (5.83, 8.27),
            "Square": (8.27, 8.27),
            "A3": (11.69, 16.54),
            "A2": (16.54, 23.39),
            "A1": (23.39, 33.11),
        }
        width, height = page_sizes[page_size]

    # Layer selection
    st.subheader("Select Layers")

    layers = {
        # "hillshade": st.checkbox("Hillshade", value="hillshade" in style),
        "building": st.checkbox("Buildings", value="building" in style),
        "streets": st.checkbox("Streets", value="streets" in style),
        "waterway": st.checkbox("Waterway", value="waterway" in style),
        "building": st.checkbox("Building", value="building" in style),
        "water": st.checkbox("Water", value="water" in style),
        "sea": st.checkbox("Sea", value="sea" in style),
        "forest": st.checkbox("Forest", value="forest" in style),
        "green": st.checkbox("Green", value="green" in style),
        "rock": st.checkbox("Rock", value="rock" in style),
        "beach": st.checkbox("Beach", value="beach" in style),
        "parking": st.checkbox("Parking", value="parking" in style),
    }

    # Hillshade parameters
    if False:  # layers["hillshade"]:
        st.subheader("Hillshade Parameters")
        azdeg = st.number_input(
            "Azimuth (degrees)", min_value=0, max_value=360, value=315
        )
        altdeg = st.number_input(
            "Altitude (degrees)", min_value=0, max_value=90, value=45
        )
        vert_exag = st.number_input("Vertical Exaggeration", min_value=0.1, value=1.0)
        dx = st.number_input("dx", min_value=0.1, value=1.0)
        dy = st.number_input("dy", min_value=0.1, value=1.0)
        alpha = st.number_input("Alpha", min_value=0.0, max_value=1.0, value=0.75)

# Add a button in a new column to the right
with cols[1]:
    for i in range(0):
        st.write("")
    button = st.button(
        "Generate",
        key="generate_map",
        help="Click to generate the map",
        type="primary",
        icon=":material/map:",
        use_container_width=True,
    )

    if button:
        hillshade_params = (
            {
                "azdeg": azdeg,
                "altdeg": altdeg,
                "vert_exag": vert_exag,
                "dx": dx,
                "dy": dy,
                "alpha": alpha,
            }
            if False  # layers["hillshade"]
            else {}
        )
        with st.spinner("Generating map..."):
            # Generate the raw map with absolutely no text or padding
            
            # Setup preset and layers
            final_layers = {k: (False if v == False else {}) for k, v in layers.items()}
            final_style = {"building": {"palette": list(custom_palette.values())}}
            
            if poster_mode:
                circular = False # Posters are square
                final_layers = {
                    'perimeter': {},
                    'water': {'tags': {'natural': ['water', 'bay'], 'waterway': ['river', 'canal']}},
                    'streets': {
                        'custom_filter': '["highway"~"motorway|trunk|primary|secondary|tertiary|residential|unclassified"]',
                        'width': {
                            'motorway': 1.5, 'trunk': 1.5, 'primary': 1, 'secondary': 0.8,
                            'tertiary': 0.5, 'residential': 0.3, 'unclassified': 0.3,
                        }
                    }
                }
                final_style = {
                    'background': {'fc': '#000000', 'ec': '#000000', 'lw': 0, 'zorder': -1},
                    'perimeter': {'fc': '#000000', 'ec': '#000000', 'lw': 0, 'zorder': 0},
                    'water': {'fc': '#ffffff', 'ec': '#ffffff', 'lw': 0, 'zorder': 1},
                    'streets': {'fc': '#ffffff', 'ec': '#ffffff', 'alpha': 1, 'lw': 0, 'zorder': 2},
                }

            fig, ax = plt.subplots(figsize=(width, height), dpi=300)
            plot_result = prettymaps.plot(
                query,
                radius=1000 * radius,
                circle=circular,
                layers=final_layers,
                style=final_style,
                figsize=(width, height),
                preset=selected_preset if not poster_mode else 'default',
                show=False,
                credit=False,
                ax=ax,
            )

            
            # Remove all axes styling completely
            ax.axis('off')
            
            raw_buf = io.BytesIO()
            plt.savefig(raw_buf, format="png", bbox_inches="tight", pad_inches=0, dpi=150)
            raw_buf.seek(0)
            
            
            # Use Pillow to construct the final image with exact pixel alignment
            from PIL import Image, ImageDraw, ImageFont
            import builtins
            
            map_img = Image.open(raw_buf)
            map_w, map_h = map_img.size
            
            if poster_mode:
                top_margin = int(map_h * 0.25)
                bottom_margin = int(map_h * 0.05)
                side_margin = int(map_w * 0.05)
                
                final_w = map_w + (side_margin * 2)
                final_h = map_h + top_margin + bottom_margin
                final_img = Image.new("RGB", (final_w, final_h), "#000000")
                final_img.paste(map_img, (side_margin, top_margin))
                draw = ImageDraw.Draw(final_img)
                
                display_title = query.split(',')[0].upper() if isinstance(query, str) else "MAP"
                subtitle = "POSTER"
                if len(query.split(',')) > 1:
                     subtitle = query.split(',')[1].strip().upper()
                
                try:
                    font_title = ImageFont.truetype("DejaVuSerif-Bold.ttf", int(final_w * 0.12))
                    font_sub = ImageFont.truetype("DejaVuSerif.ttf", int(final_w * 0.03))
                except:
                    font_title = ImageFont.load_default(size=48) if hasattr(ImageFont, 'load_default') and 'size' in ImageFont.load_default.__code__.co_varnames else ImageFont.load_default()
                    font_sub = ImageFont.load_default(size=24) if hasattr(ImageFont, 'load_default') and 'size' in ImageFont.load_default.__code__.co_varnames else ImageFont.load_default()
                
                bbox_title = draw.textbbox((0, 0), display_title, font=font_title)
                x_title = (final_w - (bbox_title[2] - bbox_title[0])) / 2
                draw.text((x_title, top_margin * 0.2), display_title, fill="#ffffff", font=font_title)
                
                bbox_sub = draw.textbbox((0, 0), subtitle, font=font_sub)
                x_sub = (final_w - (bbox_sub[2] - bbox_sub[0])) / 2
                draw.text((x_sub, (top_margin * 0.2) + (bbox_title[3] - bbox_title[1]) + (top_margin * 0.1)), subtitle, fill="#ffffff", font=font_sub)

            else:
                top_margin = 60
                bottom_margin = 40
                side_margin = 40
                
                final_w = map_w + (side_margin * 2)
                final_h = map_h + top_margin + bottom_margin
                final_img = Image.new("RGB", (final_w, final_h), "white")
                final_img.paste(map_img, (side_margin, top_margin))
                draw = ImageDraw.Draw(final_img)
                
                display_title = query.split(',')[0].upper() if isinstance(query, str) else "MAP"
                font_title = ImageFont.load_default(size=24) if hasattr(ImageFont, 'load_default') and 'size' in ImageFont.load_default.__code__.co_varnames else ImageFont.load_default()
                font_footer = ImageFont.load_default(size=12) if hasattr(ImageFont, 'load_default') and 'size' in ImageFont.load_default.__code__.co_varnames else ImageFont.load_default()
                
                draw.text((side_margin, 20), display_title, fill="#2F3737", font=font_title)
                draw.text((side_margin, top_margin + map_h + 10), "Map data © OpenStreetMap contributors | Generated by Prettymaps", fill="#475657", font=font_footer)
            
            final_buf = io.BytesIO()
            final_img.save(final_buf, format="PNG")
            final_buf.seek(0)
            
            st.session_state.last_image = final_buf

            # Save the figure to a file
            fig_path = "/tmp/generated_map.png"
            with open(fig_path, "wb") as f:
                f.write(st.session_state.last_image.getbuffer())

            # Save SVG for persistent download
            svg_path = download_svg()
            st.session_state.last_png_path = fig_path
            st.session_state.last_svg_path = svg_path

    # Always show download buttons (disabled if no image)
    png_ready = "last_png_path" in st.session_state and os.path.exists(
        st.session_state["last_png_path"]
    )
    svg_ready = "last_svg_path" in st.session_state and os.path.exists(
        st.session_state["last_svg_path"]
    )
    btn_cols = st.columns(2)
    with btn_cols[0]:
        st.download_button(
            label="Download PNG",
            data=open(st.session_state["last_png_path"], "rb") if png_ready else b"",
            file_name=f"{query}.png",
            mime="image/png",
            use_container_width=True,
            disabled=not png_ready,
        )
    with btn_cols[1]:
        st.download_button(
            label="Download SVG",
            data=open(st.session_state["last_svg_path"], "rb") if svg_ready else b"",
            file_name=f"{query}.svg",
            mime="image/svg",
            use_container_width=True,
            disabled=not svg_ready,
        )

    # Always show image (generated or placeholder)
    if st.session_state.get("last_image"):
        st.image(st.session_state.last_image, use_container_width=True)
    else:
        st.image(
            "https://github.com/marceloprates/prettymaps/blob/main/pictures/app_placeholder.png?raw=true",
            use_container_width=True,
        )
