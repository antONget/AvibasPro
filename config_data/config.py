from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: str
    support_id: int
    redis_url: str
    yookassa_id: int
    yookassa_key: str
    username_avibus: str
    password_avibus: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admin_ids=env('ADMIN_IDS'),
                               support_id=env('SUPPORT_ID'),
                               redis_url=env('REDIS_URL'),
                               yookassa_id=env('YOOKASSA_ID'),
                               yookassa_key=env('YOOKASSA_KEY'),
                               username_avibus=env('USERNAME_AVIBUS'),
                               password_avibus=env('PASSWORD_AVIBUS')))
