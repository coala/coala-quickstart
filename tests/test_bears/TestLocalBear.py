from coalib.bears.LocalBear import LocalBear


class TestLocalBear(LocalBear):
    CAN_FIX = {}
    LANGUAGES = {}

    def run(self, filename, file, yield_results=False):
        if yield_results:
            yield 1
