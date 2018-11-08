from BaseItem import  iimediaItem


class iMqIMDataTaskListItem(iimediaItem):
    plat_id = iimediaItem.Field()
    task_id = iimediaItem.Field()
    obj_id  = iimediaItem.Field()
    obj_name= iimediaItem.Field()
    obj_code= iimediaItem.Field()
    create_time = iimediaItem.Field()
    sn      = iimediaItem.Field()



class iMqIMDataCollectItem(iMqIMDataTaskListItem):
    process_code = iimediaItem.Field()
    data         = iimediaItem.Field()
    report_time  = iimediaItem.Field()
    stat         = iimediaItem.Field()
    note         = iimediaItem.Field()

if __name__ == '__main__':
    p = iMqIMDataCollectItem()
    p.sn = '''456'''
    p.report_time = 2018
    print(p())