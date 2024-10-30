class Renderable:
    def render(self):
        raise NotImplementedError("Subclasses must implement render method")

    def add_to_layer(self, layer):
        layer.append(self)
