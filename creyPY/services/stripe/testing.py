class ItemReturn:
    quantity = 1


class SubscriptionItem:
    def retrieve(self, id: str = ""):
        return ItemReturn

    def modify(self, id: str, quantity: int):
        return ItemReturn


class StripeAPI:
    def __init__(self, key: str):
        pass

    @property
    def SubscriptionItem(self):
        return SubscriptionItem


def get_stripe_api():
    return StripeAPI("test")
