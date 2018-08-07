class DataCleaner:

    def __init__(self):
        pass

    @staticmethod
    def get_temp_filelist():
        return []

    def end(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end()
