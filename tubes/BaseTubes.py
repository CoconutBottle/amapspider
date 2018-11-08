class BaseTubes(object):
    def __init__(self, platid=None, taskid=None, objid=None):
        self.plat_id = platid
        self.task_id = taskid
        self.obj_id = objid
        self.stat   = 1
        self.note   = None

    def tubes_allchannel(self):
        pass

    def tubes_menus(self, code):
        pass

    def tubes_detail(self, code):
        pass

