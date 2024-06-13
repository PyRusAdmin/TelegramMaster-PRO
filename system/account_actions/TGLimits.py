from loguru import logger

from system.auxiliary_functions.global_variables import ConfigReader
from system.sqlite_working_tools.sqlite_working_tools import DatabaseHandler


class SettingLimits:
    """������ �� �������� TelegramMaster"""

    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.config_reader = ConfigReader()
        self.account_limits = self.config_reader.get_limits()
        self.account_limits_none = None

    async def get_usernames_with_limits(self, table_name):
        """��������� ������ ������������� �� ���� ������ � ������ �������"""
        logger.info(f"����� �� �������: {self.account_limits}")
        number_usernames: list = await self.db_handler.open_db_func_lim(table_name=table_name,
                                                                        account_limit=self.account_limits)
        logger.info(f"����� username: {len(number_usernames)}")
        return number_usernames

    async def get_usernames_without_limits(self, table_name):
        """��������� ������ ������������� �� ���� ������ ��� ����� �������"""
        logger.info(f"����� �� ������� (��� �����������)")
        number_usernames: list = await self.db_handler.open_db_func_lim(table_name=table_name,
                                                                        account_limit=self.account_limits_none)
        logger.info(f"����� username: {len(number_usernames)}")
        return number_usernames
