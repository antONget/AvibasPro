import logging

import yookassa
from yookassa import Payment, Refund
import uuid
from config_data.config import Config, load_config

config: Config = load_config()
yookassa.Configuration.account_id = config.tg_bot.yookassa_id
yookassa.Configuration.secret_key = config.tg_bot.yookassa_key


def create_payment(amount: str, description: str, full_name: str, user_tg_id: int,
                   message_order_id: int, email: str, phone: str):
    """
    Чтобы принять оплату, необходимо создать объект платежа — Payment. Он содержит всю необходимую информацию
     для проведения оплаты (сумму, валюту и статус). У платежа линейный жизненный цикл, он последовательно
      переходит из статуса в статус.
    :param amount: Сумма платежа. Иногда партнеры ЮKassa берут с пользователя дополнительную комиссию,
     которая не входит в эту сумму.
    :param description: Описание транзакции (не более 128 символов), которое вы увидите в личном кабинете ЮKassa,
     а пользователь — при оплате. Например: «Оплата заказа № 72 для user@yoomoney.ru».
    :param full_name:
    :param user_tg_id:
    :param message_order_id:
    :param email:
    :param phone:
    :return:
    """
    logging.info(f"create_payment {amount} {full_name} {email} {phone} {description}")
    id_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/AviBusProBot"
        },
        "description": 'Билет на автобус',
        "receipt": {
            "customer": {
                "full_name": full_name,
                "email": email,
                "phone": phone
            },
            "items": [
                {
                    "description": description,
                    "quantity": 1,
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": 1,
                    "payment_mode": "full_payment",
                    "payment_subject": "service"
                },
            ]
        }
    }, id_key)
    # print(payment.confirmation.confirmation_url)
    return payment.confirmation.confirmation_url, payment.id


def check_payment(payment_id: str):
    logging.info('check_payment')
    payment = yookassa.Payment.find_one(payment_id)
    """
    pending — счет создан и ожидает успешной оплаты;
    succeeded — счет успешно оплачен, есть связанный платеж в статусе succeeded 
    (финальный и неизменяемый статус для платежей в одну стадию);
    canceled — вы отменили счет, успешный платеж по нему не поступил или был отменен 
    (при оплате в две стадии) либо истек срок действия счета (финальный и неизменяемый статус).
    """
    return payment.status


def refund_ticket(amount: str, payment_id: str):
    """
    Чтобы сделать полный возврат, в запросе на создание возврата  передайте уникальный идентификатор
     (payment_id) и сумму (amount) возвращаемого платежа.
    :param amount:
    :param payment_id:
    :return:
    """
    logging.info('refund_ticket')
    refund = Refund.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "payment_id": payment_id
    })
    return refund
