from coalib.bears.LocalBear import LocalBear


class LanguageSettingBear(LocalBear):
    CAN_FIX = {}
    LANGUAGES = {'All'}

    def run(self, filename, file, language: str):
        pass
