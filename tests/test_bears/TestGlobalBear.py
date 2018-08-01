from coalib.bears.GlobalBear import GlobalBear


class TestGlobalBear(GlobalBear):
    CAN_FIX = {}
    LANGUAGES = {}

    def run(self, yield_results=False):
        if yield_results:
            yield 1
