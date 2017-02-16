from xii import error


def prepare_store(defn, store):
    # parse xii global header
    if "xii" in defn:
        for key, value in defn["xii"].items():
            store.set("global/" + key, value)

    for ctype, cname, component in get_components(defn):
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
        component["basename"] = name

        if "count" in component and component["count"] > 1:
            tmp = dict(component)
            del tmp["count"]
            for i in range(1, component["count"]+1):
                yield (ctype, "{}-{}".format(name, i), tmp)
        else:
            yield (ctype, name, component)
