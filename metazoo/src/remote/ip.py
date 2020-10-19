# Execute on main or secondary DAS5 node to get infiniband ip address for given node number
def node_to_infiniband_ip(node_nr):
    return '10.149.'+('{:03d}'.format(node_nr)[0])+'.'+'{:03d}'.format(node_nr)[1:]
