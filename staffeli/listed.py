from staffeli import names


def _lookup_id(id, entities):
    for entity in entities:
        if entity['id'] == id:
            return entity

    ids = ["{} ({})".format(entity['id'], entity['name'])
           for entity in entities]
    raise LookupError(
        "No candidate for {}. Your options include {}.".format(
            id, ", ".join(ids)))


def _lookup_name(name, entities):
    matches = []

    for entity in entities:
        if name.lower() in entity['name'].lower():
            matches.append(entity)

    if len(matches) > 1:
        matching_names = [match['name'] for match in matches]
        raise LookupError(
            "Multiple candidates for \"{}\": {}.".format(
                name, names.pp(matching_names)))

    if len(matches) == 0:
        all_names = [entity['name'] for entity in entities]
        raise LookupError(
            "No candidate for \"{}\". Your options include {}.".format(
                name, names.pp(all_names)))

    return matches[0]


class ListedEntity:
    def __init__(self, entities=None, name=None, id=None):
        if entities is not None:
            if name is not None:
                self.json = _lookup_name(name, entities)
            elif id is not None:
                self.json = _lookup_id(id, entities)
            else:
                raise LookupError(
                    "For me to find a course, you must provide a name or id.")
        if self.json is not None:
            self.id = self.json['id']
            self.displayname = self.json['name']
        else:
            raise TypeError(
                "ListedEntity initialized with insufficient data")
