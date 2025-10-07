import nest_asyncio
nest_asyncio.apply()

from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3 as v3
from trame.widgets import vtk as vtk_widgets
import pyvista as pv
from pyvista.trame.ui import plotter_ui
import pandas as pd
import pyarrow.parquet as pq
import os
current_dir = os.getcwd() 

# Load workbook
xlsx_path = os.path.join(current_dir,"EliteDangrous_IGAU_CrystalQuest" ,"Tree Sites.xlsx")

# Read all three sheets into separate DataFrames
sheet_names = ["Sites"]  # add more if reading multiple sheets 
dfs = pd.read_excel(xlsx_path, sheet_name=sheet_names) 

# Access individual DataFrames
Sites_df = dfs["Sites"] # get the required sheet from dfs 

#load Systems stars and planets 
# Read entire file into a Table
system_table_path = os.path.join(current_dir,"EliteDangrous_IGAU_CrystalQuest" , "Cache2","subset_systemdata.parquet")
star_table_path = os.path.join(current_dir, "EliteDangrous_IGAU_CrystalQuest" ,"Cache2","subset_stars.parquet")
planet_table_path = os.path.join(current_dir, "EliteDangrous_IGAU_CrystalQuest" ,"Cache2","subset_planets.parquet")

system_table = pq.read_table(system_table_path)
star_table = pq.read_table(star_table_path)
planet_table = pq.read_table(planet_table_path)

# Convert to pandas 
system_df = system_table.to_pandas()
planet_df = planet_table.to_pandas()
star_df = star_table.to_pandas()

#flatten the coords and add back to system_df
coords_df = pd.DataFrame(system_df["coords"].tolist(), index=system_df.index)
coords_df.columns = ["x", "y", "z"]
system_df = pd.concat([system_df.drop(columns=["coords"]), coords_df], axis=1)

#Now we want to find the system names that are in teh sites dataframe and systems_df
# Set all names to lower case 
# Lowercase system names in each
system_df["name_lower"] = system_df["name"].str.lower()
Sites_df["system_name_lower"] = Sites_df["System_Name"].str.lower()

#find the matches 
sites_merged_df = Sites_df.merge(
    system_df[["name_lower", "systemId64", "x", "y", "z"]],
    left_on="system_name_lower",
    right_on="name_lower",
    how="left"
)
#clean up 
sites_merged_df = sites_merged_df.drop(columns=["name_lower", "system_name_lower"])

#now we have all the data we wil find all the unique crystal types 
crystal_cols = ["CrystalsNSP1", "CrystalsNSP2", "CrystalsNSP3"]

# Stack the three columns into one series, drop missing, lower‐case to catch "none"
all_crystals = (
    sites_merged_df[crystal_cols]
    .stack()
    .dropna()
    .str.strip()
    .str.lower()
)

# Filter out the literal "none" and get uniques
unique_crystals = sorted({c for c in all_crystals if c != "none"})
print(unique_crystals)

#set list for tree types 
tree_types=['both','pods']
tree_cols = ["TreePodsNSP1", "TreePodsNSP2", "TreePodsNSP3"]

# Fill NaN with empty string, then lowercase
sites_merged_df[tree_cols] = (
    sites_merged_df[tree_cols]
    .fillna("")              # Replace NaN → ""
    .apply(lambda col: col.str.lower())
)

#We will now get all the brown dwarf systems and plot as a point cloud 
# Filter stars for subtype == 'Y (brown dwarf) Star' (case‐insensitive)
mask_bd = star_df["subType"].str.strip().str.lower() == "y (brown dwarf) star".lower()
bd_df = star_df.loc[mask_bd, ["systemId64"]]

#Get unique systemId64 values (to avoid duplicate points)
bd_systems = bd_df.drop_duplicates()

#Join to system_df to pull in x,y,z
bd_coords = (
    bd_systems
    .merge(
        system_df[["systemId64", "x", "y", "z"]],
        on="systemId64",
        how="left"
    )
    .dropna(subset=["x", "y", "z"])     # drop any with missing coords
)
bd_points = bd_coords[["x", "y", "z"]].values

# now get all systems and create a point cloud
allsystems_points = system_df[["x", "y", "z"]].to_numpy()

# set up style sheets for plotting 
CRYSTAL_STYLES = {
    "albidium ice": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "white",
        "opacity": 0.5,
        "ambient": 0.3,
        "diffuse": 0.5,
        "specular": 0.6,
        "specular_power": 20,
        "lighting": True,
    },
    
    "flavum silicate": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "blue",
        "opacity": 0.5,
        "ambient": 0.1,
        "diffuse": 0.8,
        "specular": 1.0,
        "specular_power": 50,
        "lighting": True,
    },
    "lindigoticum ice": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "white",
        "opacity": 0.5,
        "ambient": 0.2,
        "diffuse": 0.7,
        "specular": 0.3,
        "specular_power": 10,
        "lighting": True,
    },
    "lindigoticum silicate": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "blue",
        "opacity": 0.5,
        "ambient": 0.2,
        "diffuse": 0.7,
        "specular": 0.3,
        "specular_power": 10,
        "lighting": True,
    },
    "prasinum ice": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "white",
        "opacity": 0.5,
        "ambient": 0.2,
        "diffuse": 0.7,
        "specular": 0.3,
        "specular_power": 10,
        "lighting": True,
    },
    
    "prasinum silicate": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "blue",
        "opacity": 0.5,
        "ambient": 0.2,
        "diffuse": 0.7,
        "specular": 0.3,
        "specular_power": 10,
        "lighting": True,
    },
    
    "purpureum ice": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "white",
        "opacity": 0.5,
        "ambient": 0.2,
        "diffuse": 0.7,
        "specular": 0.3,
        "specular_power": 10,
        "lighting": True,
    },
    
    "rubeum ice": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "white",
        "opacity": 0.5,
        "ambient": 0.2,
        "diffuse": 0.7,
        "specular": 0.3,
        "specular_power": 10,
        "lighting": True,
    },
    
    "rubeum silicate": {
        "geom": pv.Sphere(radius=12, theta_resolution=32, phi_resolution=32),
        "color": "blue",
        "opacity": 0.5,
        "ambient": 0.2,
        "diffuse": 0.7,
        "specular": 0.3,
        "specular_power": 10,
        "lighting": True,
    },
        
}

TREE_STYLES = {
    "both": {
        "geom": pv.Sphere(radius=6, theta_resolution=32, phi_resolution=32),
        "color": "green",
        "opacity": 1,
        "ambient": 0.3,
        "diffuse": 0.5,
        "specular": 0.6,
        "specular_power": 20,
        "lighting": True,
    },
    "pods": {
        "geom": pv.Sphere(radius=6, theta_resolution=32, phi_resolution=32),
        "color": "red",
        "opacity": 1.0,
        "ambient": 0.4,
        "diffuse": 0.8,
        "specular": 1.0,
        "specular_power": 50,
        "lighting": True,
    },
        
}




# Your Trame application logic here...
def main():
    server = get_server(client_type="vue3")
    state, ctrl = server.state, server.controller

    pl_home = pv.Plotter(off_screen=True)
    
    plotter = pv.Plotter(off_screen=True)
    plotter.set_background("black")

    #plot all the systems as a point cloud 
    allsystems_points[:, [1, 2]] = allsystems_points[:, [2, 1]]
    all_systems_cloud = pv.PolyData(allsystems_points)

    allsystems_actor = plotter.add_mesh(
        all_systems_cloud,
        color=(0.4, 0.6, 0.9),   # base blue
        style='points_gaussian',
        opacity=0.30,            # overall transparency
        point_size=1,           # in pixel units
        lighting=False          # disable lighting for pure glow
    )


    #set up the brown dwarf points 

    bd_points[:, [1, 2]] = bd_points[:, [2, 1]]
    bd_cloud = pv.PolyData(bd_points)
    bd_actor = plotter.add_points(
        bd_cloud,
        color="brown",                   # choose whatever color you like
        point_size=3,                    # adjust to taste
        render_points_as_spheres=True    # gives each point a little sphere
    )

    for treeT in tree_types:
        style = TREE_STYLES[treeT].copy()
        source = style.pop("geom")      # already a pv.PolyData
        
        pts = sites_merged_df[
           sites_merged_df[tree_cols].apply(
               lambda row: treeT in row.str.lower().tolist(), axis=1
           )
       ][["x", "z", "y"]].values

        if pts.size == 0:
           continue

        cloud_trees = pv.PolyData(pts)
        glyph_tree = cloud_trees.glyph(scale=False, geom=source)
        #glyph_tree.scale(style.pop("scale"))
        plotter.add_mesh(glyph_tree, **style)


    for cryst in unique_crystals:
        style = CRYSTAL_STYLES[cryst].copy()
        source = style.pop("geom")      # already a pv.PolyData
        
        pts = sites_merged_df[
           sites_merged_df[crystal_cols].apply(
               lambda row: cryst in row.str.lower().tolist(), axis=1
           )
       ][["x", "z", "y"]].values

        if pts.size == 0:
           continue

        
        cloud = pv.PolyData(pts)
        glyph = cloud.glyph(scale=False, geom=source)
        #glyph.scale(style.pop("scale"))
        plotter.add_mesh(glyph, **style)

    # Create a smooth sphere
    tree_sphere = pv.Sphere(radius=486,           # adjust size as needed
                              center=(17149.8, -12679.6, -148.4),
                              theta_resolution=32,
                              phi_resolution=32)

    treesphere_actor=plotter.add_mesh(
    tree_sphere,
    color='blue', # Or any color you prefer
    opacity = 0.4,
    ambient=0.8, # Increase ambient for a subtle glow
    diffuse=0.5,
    specular=0.4,
    specular_power=100, # Adjust as needed
    smooth_shading=True,
    show_edges=False # Hides the mesh edges for a smoother look
    )


    plotter.show_bounds(
        grid='back',
        location='outer',
        all_edges=True,
        xtitle='X Galactic',
        ytitle='Z Galactic',   # you’d swapped Y/Z
        ztitle='Y Galactic',
        fmt='%0.0f',           # ← a single format string
        color='white',
        font_size=16,
        minor_ticks=False
    )

    def toggle_visibility_bd(checkbox_value):
        # The point_actor is accessible within the scope of the callback function
        # You can access its properties to change its visibility
        bd_actor.visibility = checkbox_value

    plotter.add_checkbox_button_widget(callback=toggle_visibility_bd, value=True, position=(10, 10), size=20, color_on='brown')

    def toggle_visibility_sphere(checkbox_value):
        # The point_actor is accessible within the scope of the callback function
        # You can access its properties to change its visibility
        treesphere_actor.visibility = checkbox_value

    plotter.add_checkbox_button_widget(callback=toggle_visibility_sphere, value=True, position=(10, 40), size=20, color_on='blue')

    def toggle_visibility_allsystems(checkbox_value):
        # The point_actor is accessible within the scope of the callback function
        # You can access its properties to change its visibility
        allsystems_actor.visibility = checkbox_value

    plotter.add_checkbox_button_widget(callback=toggle_visibility_allsystems, value=True, position=(10, 70), size=20, color_on='white')

    bd_label_position = (10 + 25 , 11) # Adjust offset as needed
    plotter.add_text("Toggle Brown Dwarf", position=bd_label_position, font_size=8, color= 'white')

    sphere_label_position = (10 + 25 , 41) # Adjust offset as needed
    plotter.add_text("Toggle Sphere", position=sphere_label_position, font_size=8, color= 'white')

    allsystems_label_position = (10 + 25 , 71) # Adjust offset as needed
    plotter.add_text("Toggle all systems", position=allsystems_label_position, font_size=8, color= 'white')

    plotter.export_html("my_interactive_plot2.html")

    plotter.export_vtksz("crystal_scene.zip", format ="zip")  
    
    #sphere = pv.Sphere()
    #pl_home.add_mesh(sphere, color='blue', name='sphere')

    with SinglePageLayout(server, container=True) as layout:
        with layout.content:
            with v3.VContainer(fluid=True, classes="pa-0 fill-height"):
                view = plotter_ui(plotter)

    if __name__ == "__main__":
        server.start(host='0.0.0.0')

main()



