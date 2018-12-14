from BaseItem import iimediaItem

class YienItem(iimediaItem):
    time_t = iimediaItem.Field()
    value  = iimediaItem.Field()
    obj    = iimediaItem.Field()
    boxoffice    = iimediaItem.Field()
    showcount    = iimediaItem.Field()
    auidencecount= iimediaItem.Field()
    price        = iimediaItem.Field()
    moviename    = iimediaItem.Field()
    code         = iimediaItem.Field()