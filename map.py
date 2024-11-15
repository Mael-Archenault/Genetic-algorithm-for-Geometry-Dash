# Repertory:



# 1: block
# 2: spike up
# 3: little_spike up
# 4: spike down
# 5: little_spike down


class Map:
    def __init__(self, name):

        file = open("./maps/"+name+".txt", "r")

        res = []
        for line in file:
            values = line[1:-2]
            values = values.split(",")
            for i in range(len(values)):
                values[i] = int(values[i])
            res.append(values)
        self.map_list = res
