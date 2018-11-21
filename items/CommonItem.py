from BaseItem import iimediaItem

class commonItem(iimediaItem):
    freq     = iimediaItem.Field()
    objname  = iimediaItem.Field()
    channel  = iimediaItem.Field()
    data     = iimediaItem.Field()
    objcode  = iimediaItem.Field()
    chancode = iimediaItem.Field()
    plat     = iimediaItem.Field()
    ext      = iimediaItem.Field()