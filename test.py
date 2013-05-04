#coding:utf-8


class Foo(object):

    def __init__(self):
        self.Datas = list()
        pass

    def clear(self):
        del self.Datas[:]
        pass

    def add(self, data):
        self.Datas.append(data)
        pass


if __name__ == "__main__":

    foo = Foo()
    foo.add("douzifly")
    foo.add("becky")
    foo.add("f00")
    for i, f in enumerate(foo.Datas):
        print(f)

    # print(foo.Datas)
    # d = foo.Datas[:2]
    # del foo.Datas[0:2]
    # print(d)
    # print(foo.Datas)

    pass
