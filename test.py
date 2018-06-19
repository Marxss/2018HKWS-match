class A(object):
    def __init__(self, num):
        self.num = num

    # def __contains__(self, item):
    #     '''''
    #     @summary:当使用in，not in 对象的时候 ,not in 是在in完成后再取反,实际上还是in操作
    #     '''
    #
    #     if item.num==self.num:
    #         return True
    #     return False


if __name__ == "__main__":
    if 11 in A(11):
        print("True")
    else:
        print("false")
    l=[A(11),A(11),A(11)]
    print([x for x in l])
