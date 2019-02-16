from threading import Lock


class Results:
    lock = Lock()
    print_list = []

    @staticmethod
    def add(value):
        Results.print_list.append(value)
