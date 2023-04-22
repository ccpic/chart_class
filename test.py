class Animal:
    def __init__(self, kg_per_head, kg_per_leg):
        self.head = 1
        self.kg_per_head = kg_per_head
        self.kg_per_leg = kg_per_leg

    def weight(self):
        return self.head * self.kg_per_head


class Cat(Animal):
    def __init__(self, legs, kg_per_head, kg_per_leg):
        self.legs = legs
        super().__init__(kg_per_head=kg_per_head, kg_per_leg=kg_per_leg)


if __name__ == "__main__":
    # a=Animal()
    # print(a.head)

    # b=a.weight()
    #     # print(b)

    c = Cat(4, 10, 5)
    print(c.head)
