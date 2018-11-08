class iimediaItem(object):
    def __call__(self, *args, **kwargs):
        return self.__dict__

    @staticmethod
    def Field():
        return None