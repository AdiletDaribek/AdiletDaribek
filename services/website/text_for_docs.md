# Основые характеристики

В данном REST API используются три основных сервиса, а именно:  
- `ud.ingate.tech/token`: [POST](https://api.jquery.com/jquery.post/) - Принимает `login` и `password` (при необходимости можно настроить хэш в `HS256` алгоритме с солью по Вашим требованиям безопасности, но мы не видем необходимости если все работает `server-server`) и выдает [JWT TOKEN](https://jwt.io/) на 30 минут для работы с другими путями.
- `ud.ingate.tech/list`: [GET](https://api.jquery.com/jquery.get/) - Отправляет в ответ список всех домофонов и шлагбаумов.
- `ud.ingate.tech/open`: [POST](https://api.jquery.com/jquery.post/) - Приминимает в форме `controller_id`, то есть уникальный идентификационный номер контроллера и открывает его.
