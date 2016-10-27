import os

from xii import util, error


def prepare_store(defn, store):
    # parse xii global header
    if "xii" in defn:
        for key, value in defn["xii"].items():
            store.set("global/" + key, value)

    for ctype, cname, component in get_components(defn):
        print("adding {}/{}". format(ctype, cname))
        tmp = {} 
        tmp["settings"] = store.get("global").copy() 
        tmp.update(component)
        store.set("components/{}/{}".format(ctype, cname), tmp)


def get_components(defn):
    for name, component in defn.items():
        # skip xii global header
        if name == "xii":
            continue
        
        # skip global namespace
        if name == "xii":
            continue
        
        if "type" not in component:
            raise error.ValidatorError("{} has no type. Check your "
                                       "definition file".format(name))
        ctype = component["type"]

        if "count" in component and component["count"] > 1:
            tmp = dict(component)
            del tmp["count"]
            for i in range(1, component["count"]+1):
                yield (ctype, "{}-{}".format(name, i), tmp)
        else:
            yield (ctype, name, component)

    

# def from_file(dfn_file, conf):
#     return Definition(find_file(dfn_file), conf)


# class Definition():
#     def __init__(self, dfn_file, conf):
#         self.dfn_file = dfn_file
#         self.dfn = util.yaml_read(self.dfn_file)
#         self.conf = conf

#     def name(self):
#         base = os.path.basename(self.dfn_file)
#         return os.path.splitext(base)[0]

#     def settings(self, key, default=None, group='xii'):
#         if group not in self.dfn or key not in self.dfn[group]:
#             return default
#         return self.dfn[group][key]

#     def name_separator(self):
#         if 'xii' in self.dfn:
#             if 'seperator' in self.dfn['xii']:
#                 return self.dfn['xii']['seperator']
#         return '-'

#     def items(self):
#         for (name, item) in self.dfn.items():
#             # skip global namespace
#             if name == "xii":
#                 continue

#             if 'count' in item:
#                 if item['count'] == 1:
#                     yield (name, item)
#                 else:
#                     for i in range(1, item['count']+1):
#                         yield ("{}-{}".format(name, i), item)
#             else:
#                 yield (name, item)

#     def item(self, name, item_type=None):
#         for (item_name, item) in self.items():
#             if item_name == name:
#                 if item_type:
#                     if item_type == item["type"]:
#                         return item
#                     return None
#                 return item
#         return None


#     def validate(self):
#         for name, settings in self.items():
#             if 'type' not in settings:
#                 raise error.InvalidAttribute(self.dfn_file, 'type', name)

#     def file_path(self):
#         return self.dfn_file
