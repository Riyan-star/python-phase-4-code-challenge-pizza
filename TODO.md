# TODO List for Flask API Implementation

## Models Update
- [x] Add relationships to Restaurant, Pizza, and RestaurantPizza models
- [x] Configure cascade deletes for RestaurantPizza
- [x] Add serialization rules to limit recursion depth
- [x] Add validation for RestaurantPizza price (1-30)

## Routes Implementation
- [x] Implement GET /restaurants route
- [x] Implement GET /restaurants/<int:id> route
- [x] Implement DELETE /restaurants/<int:id> route
- [x] Implement GET /pizzas route
- [x] Implement POST /restaurant_pizzas route

## Followup Steps
- [ ] Run database migrations and seed the database
- [ ] Run tests with pytest -x
- [ ] Test the API using Postman or React frontend
