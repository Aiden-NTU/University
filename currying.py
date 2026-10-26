from toolz import curry
from toolz.curried import pipe, filter, map, get, compose_left

orders = [
    {"id": 1, "status": "paid",      "total": 100.0, "country": "UK"}, 
    {"id": 2, "status": "pending",   "total":  50.0, "country": "UK"},
    {"id": 3, "status": "paid",      "total": 200.0, "country": "US"},
    {"id": 4, "status": "paid",      "total":  80.0, "country": "UK"},
    {"id": 5, "status": "cancelled", "total": 120.0, "country": "US"},
]

# ---------- Part 1 ----------
@curry
def apply_discount(rate, price):  return price * (1 - rate)

ten_percent_off = apply_discount(0.10)   # gave 1 of 2 -> no error, returns a function waiting for price
print(ten_percent_off(100))              # gave the 2nd (price=100) -> body runs -> 90.0

# ---------- Part 2 ----------
@curry
def field_equals(key, value, record):  return record[key] == value         

result = pipe(
    orders, ## Pass the dict of orders
    filter(field_equals(key="status", value="paid")), ## Call the filter. This is the curried filter variant, meaning it is able to wait for further values
                                                      ## In this case we tell it we are giving the key and value params, but it doesn't know the record value
                                                      ## So python takes the orders dict to fill in the record value.
                                                      ## The 3 required params are then resolved, and it executes immediately.

                                                      ## NOTE : Python actually evaluates this line first, before the pipe itself and before the orders is declared, because python evaluates inside-out
                                                      ## As a result of this, status and paid are assigned to key and value, in that order, if i were to not include the keyword arguments, so the explicit keyword arguments here are not required
                                                      ## But it's best practice to label the keyword arguments where you can, rather than assume a developer can figure out what order values go into the params.

    filter(field_equals(key="country", value="UK")),  ## Now that the orders dict is filtered, it is passed again as the filtered version, to this new filter, 
                                                      ## and the same happens again, returning a further filtered dict
                                                      ## This happens because pipe acts like a treadmill, it takes whatever value is returned from the last called argument and passes it to the next

                                                      ## NOTE : Here we are using the map and get curried variants, which means we are able to pass the "total" as the first param, but we let it await the evaluation of the iterable it works on.
                                                      ## The signature of the map function is func, iterable; In this case applying the get to the function call, where get only requires itself, and then awaiting the iterable which is returned by the filter
                                                      ## If we wanted this the other way around, we could pass keyword arguments so that the iterable is filled first and then python places the passed function later.

    map(get("total")),                                ## Now return a list of the total values from the filtered dict given by the last filter. 
    map(apply_discount(0.10)),                        ## Now apply the discount to each total value and return a list
    sum,                                              ## Now return the sum of the total discounted value. NOTE: This call doesn't require currying because we are only passing a single value.
                                                      ## The inbuilt sum does have the ability to take an extra parameter; Specifically a start parameter, but the signature for the sum param is 'sum(iterable, /, start=0)'
                                                      ## This / symbol means that python requires anything after that symbol to pass its keyword argument.
)

print(result)

# ---------- Part 3 ----------
@curry
def shipping_cost(weight_kg, distance_km, rate):  return weight_kg * distance_km * rate

step = shipping_cost(distance_km=120)   # 1 of 3 given, by name -> waiting for weight_kg and rate
step = step(rate=0.02)                  # 2 of 3 given -> waiting for weight_kg
print(step(weight_kg=5))                # 3 of 3 -> body runs -> 12.0

# ---------- Stretch ----------
uk_paid_revenue = compose_left(         # same chain as pipe, but with no data yet
    filter(field_equals("status", "paid")),     # (same five steps as above)
    filter(field_equals("country", "UK")),
    map(get("total")),
    map(apply_discount(0.10)),
    sum,
)
# compose_left returns ONE function that waits for the starting list.
print(uk_paid_revenue(orders))          # you pass `orders` here instead of inside pipe -> 162.0