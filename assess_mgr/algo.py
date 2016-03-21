# coding:utf8
'''
Created on 2015-10-14

@author: yechengzhou
'''


from multiprocessing import Process, Queue
import models

class Algo(object):

    def __init__(self, source_x_list = [], source_y_list = []):
        if len(source_x_list) != len(source_y_list):
            raise algoException('source x and source y should have same length')
        if len(source_x_list) < 2 or len(source_y_list ) < 2:
            raise algoException('please provide at least 2 source data')
        self.x_source = [int(x) for x in source_x_list]
        self.y_source = [int(y) for y in source_y_list]

    def linear(self):
        """
        :return:(a,b) y = ax + b
        """
        source_x = self.x_source
        source_y = self.y_source

        average_x=float(sum(source_x))//len(source_x)
        average_y=float(sum(source_y))/len(source_y)
        x_sub=map((lambda x:x-average_x),source_x)
        y_sub=map((lambda x:x-average_y),source_y)
        x_sub_pow2=map((lambda x:x**2),x_sub)
        x_y=map((lambda x,y:x*y),x_sub,y_sub)
        if sum(x_sub_pow2) == 0:
            print source_x
            a=round((source_y[-1]-source_y[0])/(source_x[-1]-source_x[0]),2)
        else:
            a=round(float(sum(x_y))/sum(x_sub_pow2),2) # 小数点后两位
        b=round(average_y-a*average_x,2)

        return (a,b)


    def curve(self, n):
        """
        :return: (a1,a2...an) y = a1x^n + a2x^(n-1) ... + an
        """
        pass


class algoException(Exception):
    def __init__(self,msg):
        self.msg = msg

    def get_msg(self):
        return self.msg


def set_algo_info(module , scene , resource_name , x, y):
    x = [int(i) for i in x]
    y = [int(j) for j in y]
    ret = {}

    try:
        al = Algo(x,y)
    except algoException, e:
        return e.get_msg()

    (a,b) = al.linear()
    """
    import matplotlib.pyplot as plt
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.plot(x, y, '*')
    plt.plot([0,max(x) + 2],[0*a+b,(max(x) + 2)*a+b])
    plt.grid()
    #plt.show()
    target = "%s/%s" % (module, scene)


    media_dir = os.path.join(settings.MEDIA_ROOT, target)
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    #media_dir = "/Users/MLS"
    pic_path = os.path.join(media_dir, public.datetime2str(datetime.datetime.now(), "%Y%m%d%H%M%S") + ".png")

    print x, y, a, b
    plt.savefig(pic_path)
    plt.close()
    """
    ret['scatter'] = []
    ret['xaxis'] = [int(i) for i in range(max(x) + int(max(x)/4) + 1)]
    ret['line'] = [a*i + b for i in ret['xaxis']]
    ret['x'] = x
    ret['y'] = y
    ret['a'] = a
    ret['b'] = b
    ret['resource'] = resource_name
    for i in range(len(x)):
        ret['scatter'].append([x[i], y[i]])

    return ret



def set_algo_info_mp(module , scene , x, y):
    q = Queue(1)

    if q.get() == "1":
        print 'wocao'
    q.put('1')
    p = Process(target=set_algo_info, args=(module , scene , x, y,))
    p.start()
    p.join()
    q.empty()


def delete_scene_record(data):
    print data
    id = data.get('id')
    models.SceneRecord.objects.filter(id=id).delete()



