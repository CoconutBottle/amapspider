from BaseItem import iimediaItem

class CommonItem(iimediaItem):
    time_t = iimediaItem.Field()
    frequency = iimediaItem.Field()
    source = iimediaItem.Field()
    value  = iimediaItem.Field()
    code   = iimediaItem.Field()
    pcode  = iimediaItem.Field()
    ext    = iimediaItem.Field()


class RoboItem(CommonItem):
    start_time = iimediaItem.Field()
    end_time   = iimediaItem.Field()
    data       = iimediaItem.Field()
    update_time= iimediaItem.Field()
    pick_time  = iimediaItem.Field()
    is_end     = iimediaItem.Field()
    unit       = iimediaItem.Field()

