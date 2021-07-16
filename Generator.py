def modify(edge_name, latency, line, edge):
    data_width = str(edge.width)
    depth = str(edge.depth)
    addr_width = str(edge.addr_width)
    latency = str(latency)
    line_components = line.split(" ")
    new_line = "relay_station #(.DATA_WIDTH("+data_width+"), .ADDR_WIDTH("+depth+"), .DEPTH("+depth+"), .LEVEL("+str(latency)+")) "+line_components[1]
    return new_line

def generator(InputRTLPath, edge2lat, NameToEdgeMap):
    new_rtl = open("new.v", "w+")
    input_rtl = open(InputRTLPath, "r")
    lines = input_rtl.readlines()
    count = 0
    # Update lines with fifos to relay_template
    for line in lines:
        for edge_name, edge in NameToEdgeMap.items():
            if edge_name in line:
                new_line = modify(edge_name, edge2lat[edge_name], line, edge)
                lines[count] = new_line
        count+=1
    # Write the updated lines to the new RTL file
    for line in lines:
        new_rtl.write(line)