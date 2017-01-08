class Beer(object):
    """Store information about a beer."""
    def __init__(self, brew_id, beer_id, style_id, reviews,
                 brew_name = None, beer_name = None, style_name = None):
        self.brew_id = brew_id
        self.beer_id = beer_id
        self.style_id = style_id
        self.brew_name = brew_name
        self.beer_name = beer_name
        self.style_name = style_name
        self.reviews = reviews
