 pre-requisites:
 --------------
  - SQlite database should be installed
  - Flask & SQLAlchemy dependant packages should be installed

Overview:
 - Run app.py to start the application
 - Landing page will be the location details search page with the fields where in user will be able to search the existing values or can add new values
 - Once user clicks on search then results will be displayed if there are any
 - User can see Update and Delete buttons in Actions colums under search results
 - If users click on Update button then they will be redirected to update page with the existing values prepopulated. Then users can change any values and click on update.
 - If users click on Delete button then the respective record will be deleted

CRUD API details:
------------------
 
- GET APIs:
   1. /api/v1/location - Returns all the location details
   
   2./api/v1/location/<int:loc_id>/department - Returns all the department details filtered by location id
   
   3. /api/v1/location/<int:loc_id>/department/<int:depart_id>/category - Returns all the details including category filtered by location id and department id
   
   4. /api/v1/location/<int:loc_id>/department/<int:depart_id>/category/<int:catg_id>/subcategory - Returns all the details including sub category details filtered by location id, department id and category id
   
   5. /api/v1/location/<int:loc_id>/department/<int:depart_id>/category/<int:catg_id>/subcategory/<int:sub_cat_id> - Returns all the details filtered by location id, department id , category id and sub category id

- POST API:
    /api/v3/location 
      Ex: curl -i -H "Content-Type: application/json" -X POST -d '{"location_desc":"Hyderabad"}' http://localhost:5000/api/v3/location
      Here it will insert new record into location table with the description as Hyderabad

- PUT API:
    /api/v4/location
      Ex: curl -i -H "Content-Type: application/json" -X PUT -d '{"location_id":10, "location_desc":"Bangalore"}' http://localhost:5000/api/v4/location
      - This will update the location description of 10th record to Bangalore

- DELETE API:
    /api/v1/location/<int:loc_id>
     Ex: curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1/location/11
        - This will delete the 11th record in sku table first then delete the data from location table
