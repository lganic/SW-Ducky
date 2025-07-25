if __name__ == '__main__':
    geo = MapGeometry.from_file('C:\\Program Files (x86)\\Steam\\steamapps\\common\\Stormworks\\rom\\data\\tiles\\mega_island_16_4_map_geometry_OLD.bin')
    # geo.clear_all_lines() # Clear all the lines
    img = geo.render_to_image(1000)
    img.show()
    # geo.save_as('C:\\Program Files (x86)\\Steam\\steamapps\\common\\Stormworks\\rom\\data\\tiles\\mega_island_0_0_map_geometry.bin')

    # geo_2 = MapGeometry.from_file('C:\\Program Files (x86)\\Steam\\steamapps\\common\\Stormworks\\rom\\data\\tiles\\mega_island_0_0_map_geometry.bin')
    # img = geo_2.render_to_image(1000)
    # img.show()
