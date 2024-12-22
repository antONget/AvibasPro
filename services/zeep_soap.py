from zeep import Client, xsd
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
import requests
import asyncio

# Определяем учётные данные
username_test = 'wsuser'
password_test = 'sales'
username = 'Hindikainen'
password = 'By0xo3bu'
unicode_string = username
encoded_string = unicode_string.encode("utf-8")
# Указываем URL WSDL SOAP-службы
wsdl_test = 'http://dev.avibus.pro/UEEDev/ws/saleport?wsdl'
wsdl = 'https://saas.avibus.pro/a/BTMS/1120/ws/saleport?wsdl'

# Создаём сессию с базовой аутентификацией
session = requests.Session()
session.auth = HTTPBasicAuth(encoded_string, password)

# Создаём клиент Zeep с базовой аутентификацией
client = Client(wsdl, transport=Transport(session=session))

# Вызываем необходимые методы SOAP
# result = client.service.GetBusStops()
# print(result)
# bus_stop_Tikhvin = "be1cc470-e52e-11ee-92d2-d00d4cbcd401"  # Тихвин
# result = client.service.GetDestinations(Substring='',
#                                         Departure=bus_stop_Tikhvin)
# result = client.service.GetTrips(Departure="be1cc470-e52e-11ee-92d2-d00d4cbcd401",
#                                  Destination="80979b40-5d41-11ee-8668-d00d4cbcd401",
#                                  TripsDate="2024-12-10")
# print(result)


async def get_bus_stops() -> list:
    return client.service.GetBusStops()


async def get_destinations(departure: str) -> list:
    return client.service.GetDestinations(Substring='',
                                          Departure=departure)


# Получение схемы мест В ответе на GetTrips есть все данные которые необходимы для отображения списка рейсов,
# если нужна схема мест автобуса по этому рейсу, то необходимо вызвать именно для этого рейса (tripId)
# функцию GetTripSegment она вернет в том числе и схему мест. Функция GetOccupiedSeats может быть использована
# для получения занятости мест на конкретном рейсе. В итоге можно получить схему мест автобуса и список занятых мест.
async def get_trips(departure: str, destination: str, trips_date: str):
    return client.service.GetTrips(Departure=departure,
                                   Destination=destination,
                                   TripsDate=trips_date)


async def get_trips_segment(trip_id: str, departure: str, destination: str):
    trips_segment = client.service.GetTripSegment(TripId=trip_id,
                                                  Departure=departure,
                                                  Destination=destination)
    print("TRIPS_SEGMENT", trips_segment, sep='\n')
    return trips_segment


async def get_occupied_seats(trip_id: str, departure: str, destination: str, order_id: str):
    occupied_seats = client.service.GetOccupiedSeats(TripId=trip_id,
                                                     Departure=departure,
                                                     Destination=destination,
                                                     OrderId=order_id)
    print("OCCUPIED_SEATS", occupied_seats, sep='\n')
    return occupied_seats


async def start_sale_session(trip_id: str, departure: str, destination: str, order_id: str):
    return client.service.StartSaleSession(TripId=trip_id,
                                           Departure=departure,
                                           Destination=destination,
                                           OrderId=order_id)


async def add_tickets(order_id: str, fare_name: str, seat_num: int, parent_ticket_seat_num: int):
    TicketSeats = client.get_type('ns0:TicketSeats')
    add_ticket = client.service.AddTickets(OrderId=order_id,
                                           TicketSeats=TicketSeats(Elements={"FareName": fare_name,
                                                                             "SeatNum": seat_num,
                                                                             "ParentTicketSeatNum":
                                                                                 parent_ticket_seat_num}))
    print(add_ticket)
    return add_ticket


async def set_ticket_data(order_id: str, number: str, seat_num: int, fare_name: str, name: str, document_number: str,
                          document: str, birthday: str, gender: str, citizenship: str):
    Tickets = client.get_type('ns0:Tickets')
    ticket_data = client.service.SetTicketData(OrderId=order_id,
                                               Tickets=Tickets(Elements={"Number": number,
                                                                         "SeatNum": seat_num,
                                                                         "FareName": fare_name,
                                                                         "PersonalData": [{"Name": "ФИО",
                                                                                           "Value": name},
                                                                                          {"Name": "Удостоверение",
                                                                                           "Value": document_number,
                                                                                           "ValueKind": document},
                                                                                          {"Name": "Дата рождения",
                                                                                           "Value": birthday},
                                                                                          {"Name": "Пол",
                                                                                           "Value": gender},
                                                                                          {"Name": "Гражданство",
                                                                                           "Value": citizenship}]}))
    print(ticket_data)
    return ticket_data


async def reserve_order(order_id: str, name: str = "Name", phone: str = "+71112223333",
                        email: str = 'example@mail.com', comment: str = 'comment'):
    Customer = client.get_type('ns0:Customer')
    ChequeSettings = client.get_type('ns0:ChequeSettings')
    reserve = client.service.ReserveOrder(OrderId=order_id,
                                          Customer=Customer(Name=name,
                                                            Phone=phone,
                                                            Email=email,
                                                            Comment=comment),
                                          ReserveKind='',
                                          ChequeSettings=ChequeSettings(ChequeWidth=48))
    print(reserve)
    return reserve


async def payment_ticket(order_id: str, amount: str):
    PaymentItems = client.get_type('ns0:PaymentItems')
    ChequeSettings = client.get_type('ns0:ChequeSettings')
    payment = client.service.Payment(OrderId=order_id,
                                     PaymentItems=PaymentItems(Elements={"PaymentType": "PaymentCard",
                                                                         "Amount": amount}),
                                     ChequeSettings=ChequeSettings(ChequeWidth=48))
    print(payment)
    return payment


if __name__ == "__main__":
    asyncio.run(add_tickets(order_id='00000022788', fare_name='Пассажирский', seat_num=0, parent_ticket_seat_num=0))