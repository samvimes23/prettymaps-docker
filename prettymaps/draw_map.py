from prettymaps import plot

try:
    print("Generating map...")
    # The new API returns a dataclass containing .fig and .ax
    plot_result = plot(
        'Praça Ferreira do Amaral, Macau',
        preset='macao',
        circle=True,
        radius=1100,
        show=False
    )
    
    # Explicitly save the figure from the returned dataclass
    plot_result.fig.savefig('/root/prettymaps_project/test_map_fixed.png', bbox_inches='tight', pad_inches=0, dpi=300)
    print("Map generated successfully at /root/prettymaps_project/test_map_fixed.png")
except Exception as e:
    print(f"Error generating map: {e}")
