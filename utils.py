class DumpLoad:
    fields_to_dump_load: list = NotImplemented

    def dump(self) -> dict:
        data = {}
        for field in self.fields_to_dump_load:
            value = getattr(self, field)
            if isinstance(value, dict) and len(value) > 0 and isinstance(list(value.keys())[0], tuple):
                value = {f"tpl%,{k[0]},{k[1]}": v for k, v in value.items()}
            data[field] = value
        return data

    def load(self, data):
        for field in self.fields_to_dump_load:
            value = data[field]
            if isinstance(value, dict) and len(value) > 0 and isinstance(list(value.keys())[0], str) and list(value.keys())[0].startswith("tpl%"):
                value = {(int(k.split(",")[1]), int(k.split(",")[2])): v for k, v in value.items()}
            setattr(self, field, value)
