import logging

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


async def get_bus_stops() -> list[dict]:
    """
    Получение списка всех остановок
    :return:
    [{
        'Name': 'Селиваново (на СПб) трасса',
        'Code': '00-000037',
        'Id': 'cca86056-e5e4-11ee-94e0-d00d4cbcd401',
        'Country': 'РОССИЯ',
        'Region': 'Ленинградская область',
        'District': 'Волховский район',
        'Automated': True,
        'HasDestinations': True,
        'UTC': Decimal('3'),
        'GPSCoordinates': '60.204551,32.670793',
        'LocationType': 'На трассе',
        'Locality': None,
        'StoppingPlace': None,
        'Address': 'посёлок Селиваново, Россия',
        'Phone': None
    },...]
    """
    logging.info('get_bus_stops')
    bus_stops = client.service.GetBusStops()
    # print('BUS_STOPS', bus_stops, sep='\n')
    return bus_stops


async def get_destinations(departure: str) -> list[dict]:
    """
    Получение пунктов назначения для выбранной остановки
    Получение пунктов прибытия для выбранной остановки отправления возможно только для автоматизированных остановок
    (Automated=True). Метод возвращает список остановок прибытия доступных при отправлении от указанной остановки,
    при этом результат можно отфильтровать при помощи параметра substring, если указать этот параметр пустым,
    то вернется список всех доступных остановок прибытия.
    :param departure:
    :return:
    [{
        'Name': 'Бор (из СПб) трасса',
        'Code': '00-000038',
        'Id': '0c23e7a2-e5e8-11ee-94e0-d00d4cbcd401',
        'Country': 'РОССИЯ',
        'Region': 'Ленинградская область',
        'District': 'Тихвинский район',
        'Automated': True,
        'HasDestinations': True,
        'UTC': Decimal('3'),
        'GPSCoordinates': '59.770595,33.470743',
        'LocationType': 'На трассе',
        'Locality': None,
        'StoppingPlace': None,
        'Address': 'деревня Бор',
        'Phone': None
    },...]
    """
    destinations = client.service.GetDestinations(Substring='',
                                                  Departure=departure)
    # print('DESTINATIONS', destinations, sep='\n')
    return destinations


async def get_trips(departure: str, destination: str, trips_date: str):
    """
    Получение схемы мест
    В ответе на GetTrips есть все данные которые необходимы для отображения списка рейсов,
    если нужна схема мест автобуса по этому рейсу, то необходимо вызвать именно для этого рейса (tripId)
    функцию GetTripSegment она вернет, в том числе и схему мест. Функция GetOccupiedSeats может быть использована
    для получения занятости мест на конкретном рейсе. В итоге можно получить схему мест автобуса и список занятых мест.
    :param departure:
    :param destination:
    :param trips_date: формат даты 2019-03-01
    :return:
    {
    'Elements': [
        {
            'Id': 'be620c3c-af19-11ef-83d2-0a01e80df301',
            'RouteId': 'f41384f4-e625-11ee-9761-d00d4cbcd401',
            'ScheduleTripId': 'da7bb9fa-af18-11ef-83d2-0a01e80df301',
            'RouteName': 'Вознесенье — Санкт-Петербург АВ № 2, 895 , Пригородное',
            'RouteNum': '895',
            'Carrier': 'ИП Гиляев',
            'Bus': {
                'Id': '083f9dd0-e470-11ee-944a-d00d4cbcd401',
                'Model': 'HIGER KLQ6128LQ',
                'LicencePlate': 'с311ск198',
                'Name': 'HIGER KLQ6128LQ (53), с311ск198',
                'SeatsClass': 'Стандартный',
                'SeatCapacity': 53,
                'StandCapacity': 0,
                'BaggageCapacity': 53,
                'SeatsScheme': [],
                'GarageNum': None,
                'AdditionalAtrributes': []
            },
            'Driver1': 'Вяткин Игорь Александрович',
            'Driver2': None,
            'Frequency': 'Ежедневно',
            'WaybillNum': None,
            'Status': 'Waiting',
            'StatusPrint': 'Ожидается в 05:25',
            'StatusReason': None,
            'StatusComment': None,
            'StatusDate': None,
            'Departure': {
                'Name': 'Сясьстрой АС',
                'Code': '00-000035',
                'Id': '26db9652-e5e4-11ee-94e0-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.14342700,32.54062400',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'Ленинградская область, Волховский район, Сясьстройское городское поселение, Сясьстрой, Петрозаводская ул, 14Б',
                'Phone': None
            },
            'DepartureTime': datetime.datetime(2024, 12, 28, 5, 35),
            'ArrivalToDepartureTime': datetime.datetime(2024, 12, 28, 5, 25),
            'Destination': {
                'Name': 'Юшково (на СПб) трасса',
                'Code': '00-000007',
                'Id': 'f002482e-e507-11ee-893e-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.070078,32.323747',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Юшково, Россия',
                'Phone': None
            },
            'ArrivalTime': datetime.datetime(2024, 12, 28, 5, 44),
            'Distance': Decimal('15'),
            'Duration': 19,
            'TransitSeats': False,
            'FreeSeatsAmount': 49,
            'PassengerFareCost': Decimal('100'),
            'Fares': [],
            'Platform': 0,
            'OnSale': True,
            'Route': [],
            'Additional': False,
            'AdditionalTripTime': [],
            'TransitTrip': True,
            'SaleStatus': None,
            'ACBPDP': None,
            'FactTripReturnTime': None,
            'Currency': 'RUB',
            'PrincipalTaxId': None,
            'AdditionalAttributes': [],
            'CarrierData': {
                'CarrierName': 'Индивидуальный предприниматель Гиляев Михаил Викторович',
                'CarrierTaxId': '782506314950',
                'CarrierStateRegNum': '312784722000369',
                'CarrierPersonalData': [
                    {
                        'Name': 'ФИО',
                        'Caption': 'ФИО',
                        'Mandatory': False,
                        'PersonIdentifier': False,
                        'Type': 'String',
                        'ValueVariants': [],
                        'InputMask': None,
                        'Value': 'Гиляев Михаил Викторович',
                        'ValueKind': None,
                        'DefaultValueVariant': {
                            'Name': None,
                            'InputMask': None,
                            'ValueProperty1': None,
                            'ValueProperty2': None,
                            'ValueProperty3': None,
                            'ValueProperty4': None,
                            'ValueProperty5': None
                        },
                        'DocumentIssueDateRequired': None,
                        'DocumentIssueOrgRequired': None,
                        'DocumentValidityDateRequired': None,
                        'DocumentInceptionDateRequired': None,
                        'DocumentIssuePlaceRequired': None,
                        'Value1': None,
                        'Value2': None,
                        'Value3': None,
                        'Value4': None,
                        'Value5': None,
                        'Group': None,
                        'ReadOnly': None
                    },
                    {
                        'Name': 'Мобильный телефон',
                        'Caption': 'Мобильный телефон',
                        'Mandatory': False,
                        'PersonIdentifier': False,
                        'Type': 'ContactInformation',
                        'ValueVariants': [
                            {
                                'Name': 'Мобильный телефон',
                                'InputMask': None,
                                'ValueProperty1': None,
                                'ValueProperty2': None,
                                'ValueProperty3': None,
                                'ValueProperty4': None,
                                'ValueProperty5': None
                            }
                        ],
                        'InputMask': None,
                        'Value': ' +79219613191',
                        'ValueKind': None,
                        'DefaultValueVariant': {
                            'Name': 'Мобильный телефон',
                            'InputMask': None,
                            'ValueProperty1': None,
                            'ValueProperty2': None,
                            'ValueProperty3': None,
                            'ValueProperty4': None,
                            'ValueProperty5': None
                        },
                        'DocumentIssueDateRequired': None,
                        'DocumentIssueOrgRequired': None,
                        'DocumentValidityDateRequired': None,
                        'DocumentInceptionDateRequired': None,
                        'DocumentIssuePlaceRequired': None,
                        'Value1': None,
                        'Value2': None,
                        'Value3': None,
                        'Value4': None,
                        'Value5': None,
                        'Group': None,
                        'ReadOnly': None
                    }
                ],
                'CarrierAddress': '195067, г Санкт-Петербург, пр Екатерининский, д. 3, литера А, офис оф. А-217',
                'CarrierWorkingHours': '06:00 - 21:00'
            },
            'CheckMan': None
        },
        {
            'Id': 'fd510f0c-af18-11ef-83d2-0a01e80df301',
            'RouteId': 'f41384f4-e625-11ee-9761-d00d4cbcd401',
            'ScheduleTripId': '377f01e4-af18-11ef-83d2-0a01e80df301',
            'RouteName': 'Вознесенье — Санкт-Петербург АВ № 2, 895 , Пригородное',
            'RouteNum': '895',
            'Carrier': 'ИП Гиляев',
            'Bus': {
                'Id': '87070748-e470-11ee-944a-d00d4cbcd401',
                'Model': 'ZHONG TONG LCK6127H',
                'LicencePlate': 'с241ер198',
                'Name': 'ZHONG TONG LCK6127H (53), с241ер198',
                'SeatsClass': 'Стандартный',
                'SeatCapacity': 53,
                'StandCapacity': 0,
                'BaggageCapacity': 53,
                'SeatsScheme': [],
                'GarageNum': None,
                'AdditionalAtrributes': []
            },
            'Driver1': 'Москалёв Владимир Анатольевич',
            'Driver2': None,
            'Frequency': 'Ежедневно',
            'WaybillNum': None,
            'Status': 'Waiting',
            'StatusPrint': 'Ожидается в 19:45',
            'StatusReason': None,
            'StatusComment': None,
            'StatusDate': None,
            'Departure': {
                'Name': 'Сясьстрой АС',
                'Code': '00-000035',
                'Id': '26db9652-e5e4-11ee-94e0-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.14342700,32.54062400',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'Ленинградская область, Волховский район, Сясьстройское городское поселение, Сясьстрой, Петрозаводская ул, 14Б',
                'Phone': None
            },
            'DepartureTime': datetime.datetime(2024, 12, 28, 19, 55),
            'ArrivalToDepartureTime': datetime.datetime(2024, 12, 28, 19, 45),
            'Destination': {
                'Name': 'Юшково (на СПб) трасса',
                'Code': '00-000007',
                'Id': 'f002482e-e507-11ee-893e-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.070078,32.323747',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Юшково, Россия',
                'Phone': None
            },
            'ArrivalTime': datetime.datetime(2024, 12, 28, 20, 4),
            'Distance': Decimal('15'),
            'Duration': 19,
            'TransitSeats': False,
            'FreeSeatsAmount': 53,
            'PassengerFareCost': Decimal('100'),
            'Fares': [],
            'Platform': 0,
            'OnSale': True,
            'Route': [],
            'Additional': False,
            'AdditionalTripTime': [],
            'TransitTrip': True,
            'SaleStatus': None,
            'ACBPDP': None,
            'FactTripReturnTime': None,
            'Currency': 'RUB',
            'PrincipalTaxId': None,
            'AdditionalAttributes': [],
            'CarrierData': {
                'CarrierName': 'Индивидуальный предприниматель Гиляев Михаил Викторович',
                'CarrierTaxId': '782506314950',
                'CarrierStateRegNum': '312784722000369',
                'CarrierPersonalData': [
                    {
                        'Name': 'ФИО',
                        'Caption': 'ФИО',
                        'Mandatory': False,
                        'PersonIdentifier': False,
                        'Type': 'String',
                        'ValueVariants': [],
                        'InputMask': None,
                        'Value': 'Гиляев Михаил Викторович',
                        'ValueKind': None,
                        'DefaultValueVariant': {
                            'Name': None,
                            'InputMask': None,
                            'ValueProperty1': None,
                            'ValueProperty2': None,
                            'ValueProperty3': None,
                            'ValueProperty4': None,
                            'ValueProperty5': None
                        },
                        'DocumentIssueDateRequired': None,
                        'DocumentIssueOrgRequired': None,
                        'DocumentValidityDateRequired': None,
                        'DocumentInceptionDateRequired': None,
                        'DocumentIssuePlaceRequired': None,
                        'Value1': None,
                        'Value2': None,
                        'Value3': None,
                        'Value4': None,
                        'Value5': None,
                        'Group': None,
                        'ReadOnly': None
                    },
                    {
                        'Name': 'Мобильный телефон',
                        'Caption': 'Мобильный телефон',
                        'Mandatory': False,
                        'PersonIdentifier': False,
                        'Type': 'ContactInformation',
                        'ValueVariants': [
                            {
                                'Name': 'Мобильный телефон',
                                'InputMask': None,
                                'ValueProperty1': None,
                                'ValueProperty2': None,
                                'ValueProperty3': None,
                                'ValueProperty4': None,
                                'ValueProperty5': None
                            }
                        ],
                        'InputMask': None,
                        'Value': ' +79219613191',
                        'ValueKind': None,
                        'DefaultValueVariant': {
                            'Name': 'Мобильный телефон',
                            'InputMask': None,
                            'ValueProperty1': None,
                            'ValueProperty2': None,
                            'ValueProperty3': None,
                            'ValueProperty4': None,
                            'ValueProperty5': None
                        },
                        'DocumentIssueDateRequired': None,
                        'DocumentIssueOrgRequired': None,
                        'DocumentValidityDateRequired': None,
                        'DocumentInceptionDateRequired': None,
                        'DocumentIssuePlaceRequired': None,
                        'Value1': None,
                        'Value2': None,
                        'Value3': None,
                        'Value4': None,
                        'Value5': None,
                        'Group': None,
                        'ReadOnly': None
                    }
                ],
                'CarrierAddress': '195067, г Санкт-Петербург, пр Екатерининский, д. 3, литера А, офис оф. А-217',
                'CarrierWorkingHours': '06:00 - 21:00'
            },
            'CheckMan': None
        }
    ],
    'TripsDate': datetime.date(2024, 12, 28),
    'Departure': 'Сясьстрой АС',
    'Destination': 'f002482e-e507-11ee-893e-d00d4cbcd401'
    }
    """
    trips = client.service.GetTrips(Departure=departure,
                                    Destination=destination,
                                    TripsDate=trips_date)
    # print('TRIPS', trips)
    return trips


async def get_trips_segment(trip_id: str, departure: str, destination: str):
    """
    Получение информации по участку рейса
    :param trip_id:
    :param departure:
    :param destination:
    :return:
    {
    'Id': 'f9040036-af08-11ef-83d2-0a01e80df301',
    'RouteId': '0b01c94c-e625-11ee-9761-d00d4cbcd401',
    'ScheduleTripId': 'd69a1058-af08-11ef-84f3-0a01e80df301',
    'RouteName': 'Санкт-Петербург АВ № 2 — Вознесенье 895 , Пригородное',
    'RouteNum': '895',
    'Carrier': 'ИП Гиляев',
    'Bus': {
        'Id': '80c96cae-e470-11ee-944a-d00d4cbcd401',
        'Model': 'ZHONG TONG LCK6127H',
        'LicencePlate': 'н225ук198',
        'Name': 'ZHONG TONG LCK6127H (53), н225ук198',
        'SeatsClass': 'Стандартный',
        'SeatCapacity': 53,
        'StandCapacity': 0,
        'BaggageCapacity': 53,
        'SeatsScheme': [
            {
                'XPos': 1,
                'YPos': 1,
                'SeatNum': 2,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 2,
                'SeatNum': 1,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 1,
                'YPos': 4,
                'SeatNum': 3,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 5,
                'SeatNum': 4,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 6,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 2,
                'YPos': 1,
                'SeatNum': 6,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 2,
                'YPos': 2,
                'SeatNum': 5,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 2,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 2,
                'YPos': 4,
                'SeatNum': 7,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 2,
                'YPos': 5,
                'SeatNum': 8,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 1,
                'SeatNum': 10,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 2,
                'SeatNum': 9,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 3,
                'YPos': 4,
                'SeatNum': 11,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 5,
                'SeatNum': 12,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 1,
                'SeatNum': 14,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 2,
                'SeatNum': 13,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 4,
                'YPos': 4,
                'SeatNum': 15,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 5,
                'SeatNum': 16,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 1,
                'SeatNum': 18,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 2,
                'SeatNum': 17,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 5,
                'YPos': 4,
                'SeatNum': 19,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 5,
                'SeatNum': 20,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 1,
                'SeatNum': 22,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 2,
                'SeatNum': 21,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 6,
                'YPos': 4,
                'SeatNum': 23,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 5,
                'SeatNum': 24,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 7,
                'YPos': 1,
                'SeatNum': 26,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 7,
                'YPos': 2,
                'SeatNum': 25,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 7,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 7,
                'YPos': 4,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 7,
                'YPos': 5,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 8,
                'YPos': 1,
                'SeatNum': 28,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 8,
                'YPos': 2,
                'SeatNum': 27,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 8,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 8,
                'YPos': 4,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 8,
                'YPos': 5,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 9,
                'YPos': 1,
                'SeatNum': 32,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 9,
                'YPos': 2,
                'SeatNum': 31,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 9,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 9,
                'YPos': 4,
                'SeatNum': 29,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 9,
                'YPos': 5,
                'SeatNum': 30,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 1,
                'SeatNum': 36,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 2,
                'SeatNum': 35,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 10,
                'YPos': 4,
                'SeatNum': 33,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 5,
                'SeatNum': 34,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 1,
                'SeatNum': 40,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 2,
                'SeatNum': 39,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 11,
                'YPos': 4,
                'SeatNum': 37,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 5,
                'SeatNum': 38,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 1,
                'SeatNum': 44,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 2,
                'SeatNum': 43,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 12,
                'YPos': 4,
                'SeatNum': 41,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 5,
                'SeatNum': 42,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 1,
                'SeatNum': 48,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 2,
                'SeatNum': 47,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 13,
                'YPos': 4,
                'SeatNum': 45,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 5,
                'SeatNum': 46,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 1,
                'SeatNum': 53,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 2,
                'SeatNum': 52,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 3,
                'SeatNum': 51,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 4,
                'SeatNum': 49,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 5,
                'SeatNum': 50,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            }
        ],
        'GarageNum': None,
        'AdditionalAtrributes': []
    },
    'Driver1': 'Смирнов Илья Сергеевич',
    'Driver2': None,
    'Frequency': 'Ежедневно',
    'WaybillNum': None,
    'Status': 'Waiting',
    'StatusPrint': 'Ожидается в 12:05',
    'StatusReason': None,
    'StatusComment': None,
    'StatusDate': None,
    'Departure': {
        'Name': 'Сясьстрой АС',
        'Code': '00-000035',
        'Id': '26db9652-e5e4-11ee-94e0-d00d4cbcd401',
        'Country': 'РОССИЯ',
        'Region': 'Ленинградская область',
        'District': 'Волховский район',
        'Automated': True,
        'HasDestinations': True,
        'UTC': Decimal('3'),
        'GPSCoordinates': '60.14342700,32.54062400',
        'LocationType': 'В населенном пункте',
        'Locality': None,
        'StoppingPlace': None,
        'Address': 'Ленинградская область, Волховский район, Сясьстройское городское поселение, Сясьстрой, Петрозаводская ул, 14Б',
        'Phone': None
    },
    'DepartureTime': datetime.datetime(2024, 12, 28, 12, 20),
    'ArrivalToDepartureTime': datetime.datetime(2024, 12, 28, 12, 5),
    'Destination': {
        'Name': 'Лодейное Поле АС',
        'Code': '00-000058',
        'Id': '6d9b1c62-e61f-11ee-81e3-d00d4cbcd401',
        'Country': 'РОССИЯ',
        'Region': 'Ленинградская область',
        'District': 'Лодейнопольский район',
        'Automated': True,
        'HasDestinations': True,
        'UTC': Decimal('3'),
        'GPSCoordinates': '60.728850,33.554926',
        'LocationType': 'В населенном пункте',
        'Locality': None,
        'StoppingPlace': None,
        'Address': 'Лодейное Поле, проспект Урицкого, 22',
        'Phone': None
    },
    'ArrivalTime': datetime.datetime(2024, 12, 28, 13, 45),
    'Distance': Decimal('92'),
    'Duration': 100,
    'TransitSeats': False,
    'FreeSeatsAmount': 53,
    'PassengerFareCost': Decimal('400'),
    'Fares': [
        {
            'Name': 'Ручная кладь',
            'Caption': 'Ручная кладь',
            'SeatType': 'HandBaggage',
            'LowAgeLimit': 0,
            'HighAgeLimit': 0,
            'OnlyWithPassenger': False,
            'Cost': Decimal('0')
        },
        {
            'Name': 'Пассажирский',
            'Caption': 'Пассажирский',
            'SeatType': 'Passenger',
            'LowAgeLimit': 0,
            'HighAgeLimit': 0,
            'OnlyWithPassenger': False,
            'Cost': Decimal('400')
        },
        {
            'Name': 'Стоя',
            'Caption': 'Стоя',
            'SeatType': 'PassengerStand',
            'LowAgeLimit': 0,
            'HighAgeLimit': 0,
            'OnlyWithPassenger': False,
            'Cost': Decimal('400')
        },
        {
            'Name': 'Багажный',
            'Caption': 'Багажный',
            'SeatType': 'Baggage',
            'LowAgeLimit': 0,
            'HighAgeLimit': 0,
            'OnlyWithPassenger': False,
            'Cost': Decimal('0')
        }
    ],
    'Platform': 0,
    'OnSale': True,
    'Route': [
        {
            'BusStop': {
                'Name': 'Санкт-Петербург АВ № 2',
                'Code': '00-000001',
                'Id': '80979b40-5d41-11ee-8668-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Санкт-Петербург',
                'District': None,
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '59.91344100,30.35763300',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'Санкт-Петербург, набережная Обводного канала, 36',
                'Phone': None
            },
            'Distance': Decimal('0'),
            'DepartureTime': datetime.datetime(1, 1, 1, 10, 0),
            'ArrivalTime': datetime.datetime(1, 1, 1, 10, 0),
            'StopDuration': 0,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Кисельня д. остановка (из СПб)',
                'Code': '00-000008',
                'Id': 'e8cd294c-e508-11ee-92d2-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.007979,32.140228',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Кисельня, Россия',
                'Phone': None
            },
            'Distance': Decimal('110'),
            'DepartureTime': datetime.datetime(1, 1, 1, 11, 45),
            'ArrivalTime': datetime.datetime(1, 1, 1, 11, 44),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Юшково (из СПб) трасса',
                'Code': '00-000006',
                'Id': '7709b362-e507-11ee-92d2-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.069916,32.324895',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Юшково, Россия',
                'Phone': None
            },
            'Distance': Decimal('122'),
            'DepartureTime': datetime.datetime(1, 1, 1, 11, 55),
            'ArrivalTime': datetime.datetime(1, 1, 1, 11, 54),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Сясьстрой АС',
                'Code': '00-000035',
                'Id': '26db9652-e5e4-11ee-94e0-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.14342700,32.54062400',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'Ленинградская область, Волховский район, Сясьстройское городское поселение, Сясьстрой, Петрозаводская ул, 14Б',
                'Phone': None
            },
            'Distance': Decimal('137'),
            'DepartureTime': datetime.datetime(1, 1, 1, 12, 20),
            'ArrivalTime': datetime.datetime(1, 1, 1, 12, 5),
            'StopDuration': 15,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Селиваново (из СПб) трасса',
                'Code': '00-000036',
                'Id': '9e6c5fa8-e5e4-11ee-94e0-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.205214,32.673027',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'посёлок Селиваново, Россия',
                'Phone': None
            },
            'Distance': Decimal('148'),
            'DepartureTime': datetime.datetime(1, 1, 1, 12, 30),
            'ArrivalTime': datetime.datetime(1, 1, 1, 12, 29),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Потанино (из СПб) трасса',
                'Code': '00-000050',
                'Id': 'f15c16bc-e5f9-11ee-9959-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.271590,32.788283',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Потанино, Россия',
                'Phone': None
            },
            'Distance': Decimal('158'),
            'DepartureTime': datetime.datetime(1, 1, 1, 12, 40),
            'ArrivalTime': datetime.datetime(1, 1, 1, 12, 39),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Паша (из СПб) трасса',
                'Code': '00-000052',
                'Id': '5990e37a-e5fa-11ee-9959-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Волховский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.397673,33.019123',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'село Паша, Россия',
                'Phone': None
            },
            'Distance': Decimal('177'),
            'DepartureTime': datetime.datetime(1, 1, 1, 12, 55),
            'ArrivalTime': datetime.datetime(1, 1, 1, 12, 54),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Доможирово (из СПб) трасса',
                'Code': '00-000054',
                'Id': '7f588526-e5fb-11ee-9959-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Лодейнопольский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.472810,33.087262',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Доможирово, Россия',
                'Phone': None
            },
            'Distance': Decimal('186'),
            'DepartureTime': datetime.datetime(1, 1, 1, 13, 5),
            'ArrivalTime': datetime.datetime(1, 1, 1, 13, 4),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Шамокша поворот (из СПб) трасса',
                'Code': '00-000056',
                'Id': 'b92dbed8-e61e-11ee-81e3-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Лодейнопольский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.665091,33.348911',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Шамокша, Россия',
                'Phone': None
            },
            'Distance': Decimal('213'),
            'DepartureTime': datetime.datetime(1, 1, 1, 13, 25),
            'ArrivalTime': datetime.datetime(1, 1, 1, 13, 24),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Лодейное Поле АС',
                'Code': '00-000058',
                'Id': '6d9b1c62-e61f-11ee-81e3-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Лодейнопольский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.728850,33.554926',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'Лодейное Поле, проспект Урицкого, 22',
                'Phone': None
            },
            'Distance': Decimal('229'),
            'DepartureTime': datetime.datetime(1, 1, 1, 13, 55),
            'ArrivalTime': datetime.datetime(1, 1, 1, 13, 45),
            'StopDuration': 10,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Подпорожье АВ',
                'Code': '00-000059',
                'Id': 'e3223f2e-e61f-11ee-81e3-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Подпорожский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.909017,34.161079',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'Ленинградская область, Подпорожье, ул. Октябрят 10',
                'Phone': None
            },
            'Distance': Decimal('271'),
            'DepartureTime': datetime.datetime(1, 1, 1, 14, 35),
            'ArrivalTime': datetime.datetime(1, 1, 1, 14, 30),
            'StopDuration': 5,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Шеменечи поворот (из СПб) трасса',
                'Code': '00-000060',
                'Id': '3206b854-e620-11ee-9761-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Подпорожский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.890576,34.388325',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'село Шеменичи, Россия',
                'Phone': None
            },
            'Distance': Decimal('285'),
            'DepartureTime': datetime.datetime(1, 1, 1, 14, 45),
            'ArrivalTime': datetime.datetime(1, 1, 1, 14, 44),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Пертозеро (из СПб) трасса',
                'Code': '00-000062',
                'Id': 'dac52a20-e620-11ee-81e3-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Подпорожский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.904355,34.610205',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Пертозеро, Россия',
                'Phone': None
            },
            'Distance': Decimal('298'),
            'DepartureTime': datetime.datetime(1, 1, 1, 14, 55),
            'ArrivalTime': datetime.datetime(1, 1, 1, 14, 54),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Гоморовичи (из СПб) трасса',
                'Code': '00-000064',
                'Id': '69b31ba2-e621-11ee-9761-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Подпорожский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.897725,34.726775',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Гоморовичи, Россия',
                'Phone': None
            },
            'Distance': Decimal('304'),
            'DepartureTime': datetime.datetime(1, 1, 1, 15, 0),
            'ArrivalTime': datetime.datetime(1, 1, 1, 14, 59),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'дор. на Юксовичи (Родионово) (из СПб)',
                'Code': '00-000066',
                'Id': 'c31d3402-e621-11ee-81e3-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Подпорожский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.914393,35.018650',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Родионово, Россия',
                'Phone': None
            },
            'Distance': Decimal('322'),
            'DepartureTime': datetime.datetime(1, 1, 1, 15, 15),
            'ArrivalTime': datetime.datetime(1, 1, 1, 15, 14),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Шустручей (дер.Кипрушино) (из СПб) трасса',
                'Code': '00-000068',
                'Id': '616f225a-e622-11ee-9761-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Подпорожский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '60.944602,35.435393',
                'LocationType': 'На трассе',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'деревня Кипрушино, Россия',
                'Phone': None
            },
            'Distance': Decimal('347'),
            'DepartureTime': datetime.datetime(1, 1, 1, 15, 35),
            'ArrivalTime': datetime.datetime(1, 1, 1, 15, 34),
            'StopDuration': 1,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        },
        {
            'BusStop': {
                'Name': 'Вознесенье',
                'Code': '00-000070',
                'Id': '300fbd68-e623-11ee-9761-d00d4cbcd401',
                'Country': 'РОССИЯ',
                'Region': 'Ленинградская область',
                'District': 'Подпорожский район',
                'Automated': True,
                'HasDestinations': True,
                'UTC': Decimal('3'),
                'GPSCoordinates': '61.013376,35.485005',
                'LocationType': 'В населенном пункте',
                'Locality': None,
                'StoppingPlace': None,
                'Address': 'городской посёлок Вознесенье, Свирская набережная',
                'Phone': None
            },
            'Distance': Decimal('356'),
            'DepartureTime': datetime.datetime(1, 1, 1, 0, 0),
            'ArrivalTime': datetime.datetime(1, 1, 1, 15, 45),
            'StopDuration': 0,
            'DayOfTrip': 0,
            'Platform': 0,
            'BanSaleFrom': False,
            'BanSaleTo': False
        }
    ],
    'Additional': False,
    'AdditionalTripTime': [],
    'TransitTrip': True,
    'SaleStatus': None,
    'ACBPDP': None,
    'FactTripReturnTime': None,
    'Currency': 'RUB',
    'PrincipalTaxId': None,
    'AdditionalAttributes': [],
    'CarrierData': {
        'CarrierName': 'Индивидуальный предприниматель Гиляев Михаил Викторович',
        'CarrierTaxId': '782506314950',
        'CarrierStateRegNum': '312784722000369',
        'CarrierPersonalData': [
            {
                'Name': 'ФИО',
                'Caption': 'ФИО',
                'Mandatory': False,
                'PersonIdentifier': False,
                'Type': 'String',
                'ValueVariants': [],
                'InputMask': None,
                'Value': 'Гиляев Михаил Викторович',
                'ValueKind': None,
                'DefaultValueVariant': {
                    'Name': None,
                    'InputMask': None,
                    'ValueProperty1': None,
                    'ValueProperty2': None,
                    'ValueProperty3': None,
                    'ValueProperty4': None,
                    'ValueProperty5': None
                },
                'DocumentIssueDateRequired': None,
                'DocumentIssueOrgRequired': None,
                'DocumentValidityDateRequired': None,
                'DocumentInceptionDateRequired': None,
                'DocumentIssuePlaceRequired': None,
                'Value1': None,
                'Value2': None,
                'Value3': None,
                'Value4': None,
                'Value5': None,
                'Group': None,
                'ReadOnly': None
            },
            {
                'Name': 'Мобильный телефон',
                'Caption': 'Мобильный телефон',
                'Mandatory': False,
                'PersonIdentifier': False,
                'Type': 'ContactInformation',
                'ValueVariants': [
                    {
                        'Name': 'Мобильный телефон',
                        'InputMask': None,
                        'ValueProperty1': None,
                        'ValueProperty2': None,
                        'ValueProperty3': None,
                        'ValueProperty4': None,
                        'ValueProperty5': None
                    }
                ],
                'InputMask': None,
                'Value': ' +79219613191',
                'ValueKind': None,
                'DefaultValueVariant': {
                    'Name': 'Мобильный телефон',
                    'InputMask': None,
                    'ValueProperty1': None,
                    'ValueProperty2': None,
                    'ValueProperty3': None,
                    'ValueProperty4': None,
                    'ValueProperty5': None
                },
                'DocumentIssueDateRequired': None,
                'DocumentIssueOrgRequired': None,
                'DocumentValidityDateRequired': None,
                'DocumentInceptionDateRequired': None,
                'DocumentIssuePlaceRequired': None,
                'Value1': None,
                'Value2': None,
                'Value3': None,
                'Value4': None,
                'Value5': None,
                'Group': None,
                'ReadOnly': None
            }
        ],
        'CarrierAddress': '195067, г Санкт-Петербург, пр Екатерининский, д. 3, литера А, офис оф. А-217',
        'CarrierWorkingHours': '06:00 - 21:00'
    },
    'CheckMan': None
}

    """
    trips_segment = client.service.GetTripSegment(TripId=trip_id,
                                                  Departure=departure,
                                                  Destination=destination)
    # print("TRIPS_SEGMENT", trips_segment, sep='\n')
    return trips_segment


async def get_occupied_seats(trip_id: str, departure: str, destination: str, order_id: str):
    """
    Получение информации по занятым местам
    :param trip_id:
    :param departure:
    :param destination:
    :param order_id:
    :return:
    {
    'return': None,
    'Bus': {
        'Id': '80c96cae-e470-11ee-944a-d00d4cbcd401',
        'Model': 'ZHONG TONG LCK6127H',
        'LicencePlate': 'н225ук198',
        'Name': 'ZHONG TONG LCK6127H (53), н225ук198',
        'SeatsClass': 'Стандартный',
        'SeatCapacity': 53,
        'StandCapacity': 0,
        'BaggageCapacity': 53,
        'SeatsScheme': [
            {
                'XPos': 1,
                'YPos': 1,
                'SeatNum': 2,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 2,
                'SeatNum': 1,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 1,
                'YPos': 4,
                'SeatNum': 3,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 5,
                'SeatNum': 4,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 1,
                'YPos': 6,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 2,
                'YPos': 1,
                'SeatNum': 6,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 2,
                'YPos': 2,
                'SeatNum': 5,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 2,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 2,
                'YPos': 4,
                'SeatNum': 7,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 2,
                'YPos': 5,
                'SeatNum': 8,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 1,
                'SeatNum': 10,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 2,
                'SeatNum': 9,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 3,
                'YPos': 4,
                'SeatNum': 11,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 3,
                'YPos': 5,
                'SeatNum': 12,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 1,
                'SeatNum': 14,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 2,
                'SeatNum': 13,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 4,
                'YPos': 4,
                'SeatNum': 15,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 4,
                'YPos': 5,
                'SeatNum': 16,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 1,
                'SeatNum': 18,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 2,
                'SeatNum': 17,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 5,
                'YPos': 4,
                'SeatNum': 19,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 5,
                'YPos': 5,
                'SeatNum': 20,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 1,
                'SeatNum': 22,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 2,
                'SeatNum': 21,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 6,
                'YPos': 4,
                'SeatNum': 23,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 6,
                'YPos': 5,
                'SeatNum': 24,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 7,
                'YPos': 1,
                'SeatNum': 26,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 7,
                'YPos': 2,
                'SeatNum': 25,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 7,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 7,
                'YPos': 4,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 7,
                'YPos': 5,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 8,
                'YPos': 1,
                'SeatNum': 28,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 8,
                'YPos': 2,
                'SeatNum': 27,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 8,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 8,
                'YPos': 4,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 8,
                'YPos': 5,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 9,
                'YPos': 1,
                'SeatNum': 32,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 9,
                'YPos': 2,
                'SeatNum': 31,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 9,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 9,
                'YPos': 4,
                'SeatNum': 29,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 9,
                'YPos': 5,
                'SeatNum': 30,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 1,
                'SeatNum': 36,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 2,
                'SeatNum': 35,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 10,
                'YPos': 4,
                'SeatNum': 33,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 10,
                'YPos': 5,
                'SeatNum': 34,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 1,
                'SeatNum': 40,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 2,
                'SeatNum': 39,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 11,
                'YPos': 4,
                'SeatNum': 37,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 11,
                'YPos': 5,
                'SeatNum': 38,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 1,
                'SeatNum': 44,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 2,
                'SeatNum': 43,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 12,
                'YPos': 4,
                'SeatNum': 41,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 12,
                'YPos': 5,
                'SeatNum': 42,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 1,
                'SeatNum': 48,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 2,
                'SeatNum': 47,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 3,
                'SeatNum': 0,
                'AvailableFares': None
            },
            {
                'XPos': 13,
                'YPos': 4,
                'SeatNum': 45,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 13,
                'YPos': 5,
                'SeatNum': 46,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 1,
                'SeatNum': 53,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 2,
                'SeatNum': 52,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 3,
                'SeatNum': 51,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 4,
                'SeatNum': 49,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            },
            {
                'XPos': 14,
                'YPos': 5,
                'SeatNum': 50,
                'AvailableFares': 'Стоя;Ручная кладь;Пассажирский;Детский без мест;Детский;Багажный'
            }
        ],
        'GarageNum': None,
        'AdditionalAtrributes': []
    }
}

    """
    occupied_seats = client.service.GetOccupiedSeats(TripId=trip_id,
                                                     Departure=departure,
                                                     Destination=destination,
                                                     OrderId=order_id)
    # print("OCCUPIED_SEATS", occupied_seats, sep='\n')
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


async def get_available_privileges(order_id: str, ticket_number: str):
    available_privileges = client.service.GetAvailablePrivileges(OrderId=order_id,
                                                                 TicketNumber=ticket_number)
    print('AVAILABLE_PRIVILEGES', available_privileges, sep='\n')
    return available_privileges

if __name__ == "__main__":
    # asyncio.run(add_tickets(order_id='00000022788', fare_name='Пассажирский', seat_num=0, parent_ticket_seat_num=0))
    asyncio.run(get_available_privileges(order_id='00000000166', ticket_number='00000000166010'))