# Place to write general purpose functions


# Helper function to style folium clusters
# returns a JavaScript function as String
def folium_cluster_styling(color):
    return f"""
        function(cluster) {{
            var childCount = cluster.getChildCount(); 
            var c = ' marker-cluster-';
            var color = "{color}";

            // Grouping everything to one group so the cluster
            // color is the same
            if (childCount < 300) {{
                c += 'small';
            }} else if (childCount < 100) {{
                c += 'medium';
            }} else {{
                c += 'large';
            }}

            return new L.DivIcon({{
                html: '<div style="background-color:' + color + ';' +
                            'font-weight: bold;' + 
                            'text-shadow: -1px -1px 0 black, 1px -1px 0 black, ' + 
                            '-1px 1px 0 black, 1px 1px 0 black;' +
                            'color: white;">' +
                            '<span>' + childCount + '</span></div>',
                className: "marker-cluster" + c,
                iconSize: new L.Point(40, 40)
            }});
        }}
    """
