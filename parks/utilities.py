# Place to write general purpose functions


# Helper function to style folium clusters
# returns a JavaScript function as String
def folium_cluster_styling(color):
    return f"""
        function(cluster) {{
            var childCount = cluster.getChildCount();
            var color = "{color}";
            var size;

            if (childCount < 10) {{
                size = 25;
            }} else if (childCount < 25) {{
                size = 40;
            }} else if (childCount < 50) {{
                size = 60;
            }} else {{
                size = 80;
            }}

            var outerSize = size * 1.2;  // Slightly larger for outer effect

            return new L.DivIcon({{
                html: '<div style="position: relative; width:' + outerSize +
                          'px; height:' + outerSize + 'px;">' +
                          // Outer translucent circle
                          '<div style="position: absolute; top: 50%; left: 50%;' +
                                      'transform: translate(-50%, -50%);' +
                                      'width:' + outerSize + 'px;' +
                                      'height:' + outerSize + 'px;' +
                                      'border-radius: 50%;' +
                                      'background-color:' + color + ';' +
                                      'opacity: 0.3;"></div>' +
                          // Inner solid circle
                          '<div style="position: absolute; top: 50%; left: 50%;' +
                                      'transform: translate(-50%, -50%);' +
                                      'width:' + size + 'px;' +
                                      'height:' + size + 'px;' +
                                      'border-radius: 50%;' +
                                      'background-color:' + color + ';' +
                                      'display: flex; justify-content: center;' +
                                      'align-items: center;' +
                                      'font-weight: bold;' +
                                      'color: white;' +
                                      'text-shadow: -1px -1px 0 black, 1px -1px 0' +
                                      'black, ' +
                                      '-1px 1px 0 black, 1px 1px 0 black;">' +
                                      '<span style="font-size: 14px;">' + childCount +
                                      '</span></div>' +
                      '</div>',
                className: "marker-cluster",
                iconSize: new L.Point(outerSize, outerSize),
                iconAnchor: new L.Point(outerSize / 2, outerSize / 2)
            }});
        }}
    """
