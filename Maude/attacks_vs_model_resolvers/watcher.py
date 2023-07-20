
class Watcher:

    def __init__(self):
        self.variant_attack_name = ""
        self.nb_labels = 0
        self.delay = 0
        self.cname_chain_length = 0
        self.dname_chain_length = 0
        self.nb_delegations = 0

    def change_values(self, kwargs):
        """Set the new values."""
        for keyword in kwargs:
            vars(self)[keyword] = kwargs[keyword]

    def set_values_and_has_changed(self, **kwargs):
        """Set the new values and, if at least one is new, returns False."""
        # vars(self) to get the dictionary of the class
        has_changed = False
        if not all(kwargs[keyword] == vars(self)[keyword] for keyword in kwargs):
            has_changed = True

        self.change_values(kwargs)
        return has_changed


def main():
    watcher = Watcher()
    # print(vars(watcher))
    # print(watcher.__getattribute__("delay"))
    print(watcher.set_values_and_has_changed(delay=400))
    print(watcher.set_values_and_has_changed(delay=400))
    print(watcher.set_values_and_has_changed(nb_labels=10))
    print(watcher.set_values_and_has_changed(nb_labels=10))


if __name__ == "__main__":
    main()
