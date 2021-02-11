# parkingLotBackend

## APIs
For all APIs give the input in request body(in postman) and json response will be returned. Rate limiter is embedded in all APIs except 'api/setRateLimiterParams/'
and 'api/'

 1. (POST 'api/setLotSize/') Create a parking lot of given size (Takes 'size' as input, else that is configurable via ENV variable PARKING_LOT_SIZE)
 2. (POST 'api/parkCar/') Park a car (Takes 'car_no' as input) and returns slot no.
 3. (POST 'api/unparkCar/') Unpark a car (Takes 'slot_no' as input) and returns appropriate message.
 4. (POST 'api/getCarNo/') Get car no by slot no (Takes 'slot_no' as input) and returns both car no and slot no.
 5. (POST 'api/getSlotNo/') Get a slot no by car no (Takes 'car_no' as input) and returns both car no and slot no.
 6. (GET 'api/') Get all slots.
 7. (POST 'api/setRateLimiterParams/') Set rate limiter parameters (Takes 'window' and 'limit' as input)

### All APIs are rate limited by IP, max 10 request allowed per 10 seconds by default.

## Run instructions:
 1. Install python3, pip and virtual env (if not installed already)
 2. Go to folder and run -> 'python3 -m venv venv'
 3. Run 'source venv/bin/activate'
 4. Run 'pip install -r requirements.txt'
 5. Run 'python3 manage.py runserver'
 
 
