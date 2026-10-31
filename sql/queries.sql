-- 1. Получить все велосипеды
SELECT *
FROM bikes;


-- 2. Получить только доступные велосипеды
SELECT *
FROM bikes
WHERE is_available = 1;


-- 3. Найти велосипеды по модели
SELECT *
FROM bikes
WHERE model LIKE '%City%';


-- 4. Получить все аренды с информацией о велосипеде,
-- пользователе и станции
SELECT
    rentals.id AS rental_id,
    bikes.model AS bike_model,
    users.name AS user_name,
    stations.name AS station_name,
    rentals.start_time,
    rentals.is_completed
FROM rentals
JOIN bikes ON rentals.bike_id = bikes.id
JOIN users ON rentals.user_id = users.id
JOIN stations ON rentals.station_id = stations.id;


-- 5. Получить незавершённые аренды
SELECT *
FROM rentals
WHERE is_completed = 0;


-- 6. Получить завершённые аренды
SELECT *
FROM rentals
WHERE is_completed = 1;


-- 7. Посчитать количество велосипедов каждого типа
SELECT
    type,
    COUNT(*) AS bike_count
FROM bikes
GROUP BY type;


-- 8. Посчитать количество аренд каждого пользователя
SELECT
    users.name,
    COUNT(rentals.id) AS rental_count
FROM users
LEFT JOIN rentals ON users.id = rentals.user_id
GROUP BY users.id, users.name;


-- 9. Посчитать количество аренд на каждой станции
SELECT
    stations.name,
    COUNT(rentals.id) AS rental_count
FROM stations
LEFT JOIN rentals ON stations.id = rentals.station_id
GROUP BY stations.id, stations.name;


-- 10. Получить среднюю вместимость станций
SELECT AVG(capacity) AS average_capacity
FROM stations;


-- 11. Найти станции с вместимостью не менее 10 велосипедов
SELECT *
FROM stations
WHERE capacity >= 10;


-- 12. Найти велосипеды, которые ещё ни разу не брали в аренду
SELECT bikes.*
FROM bikes
LEFT JOIN rentals ON bikes.id = rentals.bike_id
WHERE rentals.id IS NULL;