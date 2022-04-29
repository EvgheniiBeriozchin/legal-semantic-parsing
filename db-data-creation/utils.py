import names
import random

def random_name():
    name_type = random.choice(range(3))
    if name_type == 0:
        return random.choice(["Mr.", "Mrs."]) + " " + names.get_last_name()
    elif name_type == 1:
        return names.get_full_name()
    else:
        if random.choice(["Mr.", "Mrs."]) == "Mr.":
            return "Mr. " + names.get_full_name(gender='male')
        else:
            return "Mrs. " + names.get_full_name(gender='female')
        
def random_names(count):
    s = ""
    for i in range(count):
        if i == 0:
            s += random_name()
        elif i == count - 1:
            s += " and " + random_name()
        else:
            s += ", " + random_name()
            
    return s

ordering = ["first", "second", "third", "fourth", "fifth"]
def random_names_partition(count, partition, partition_by_name):
    s = ""
    r_names = []
    for i in range(count):
        r_name = random_name()
        r_names.append(r_name)
        if i == 0:
            s += r_name
        elif i == count - 1:
            s += " and " + r_name
        else:
            s += ", " + r_name
            
    first_group = sorted(random.sample(range(count), k=partition))
    second_group = list(range(count))
    s1 = "" if not partition_by_name else ("one by " if partition == 1 else "ones by ")
    if partition == 1:
        s1 += (r_names[first_group[0]] if partition_by_name else ordering[first_group[0]])
    else:
        for i, index in enumerate(first_group):
            second_group.remove(index)
            sub = (r_names[index] if partition_by_name else ordering[index])
            if i == 0:
                s1 += sub
            elif i == partition - 1:
                s1 += " and " + sub
            else:
                s1 += ", " + sub
            
    s2 = "" if not partition_by_name else ("one by " if count - partition == 1 else "ones by ")
    if count - partition == 1:
        s2 += (r_names[second_group[0]] if partition_by_name else ordering[second_group[0]])
    else:
        for i, index in enumerate(second_group):
            sub = (r_names[index] if partition_by_name else ordering[index])
            if i == 0:
                s2 += sub
            elif i == count - partition - 1:
                s2 += " and " + sub
            else:
                s2 += ", " + sub
            
    return s, s1, s2